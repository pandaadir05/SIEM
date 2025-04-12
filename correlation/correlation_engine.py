#!/usr/bin/env python3
import json
import time
import os
import signal
import threading
import traceback
from kafka import KafkaConsumer, KafkaProducer
from elasticsearch import Elasticsearch
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict, deque
from datetime import datetime, timedelta

# Import from project root
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from correlation.sigma_loader import load_sigma_rules
from correlation.sigma_translator import advanced_sigma_to_python_condition

# Set up logging
log_file = os.path.join(config.LOG_DIR, "correlation.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if config.DEBUG_MODE else logging.INFO)
logger.addHandler(handler)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# Global variables
running = True
ip_events = defaultdict(lambda: deque(maxlen=10))
sigma_rules_last_reload = 0
compiled_rules = []
alert_deduplication = set()  # Store rule_id + event_hash for deduplication


class CorrelationEngine:
    def __init__(self):
        """Initialize the correlation engine."""
        self.es = self._connect_elasticsearch()
        self.consumer = self._create_consumer()
        self.producer = self._create_producer()
        self.reload_sigma_rules()
        
        # Clear deduplication cache periodically
        self.dedup_cleaner = threading.Timer(300, self._clear_deduplication_cache)
        self.dedup_cleaner.daemon = True
        self.dedup_cleaner.start()
        
    def _connect_elasticsearch(self):
        """Connect to Elasticsearch with retry logic."""
        max_retries = 5
        retry_delay = 5
        
        es_config = {
            'hosts': [config.ES_HOST],
            'retry_on_timeout': True,
            'max_retries': 3,
            'timeout': 30
        }
        
        # Add authentication if provided
        if config.ES_USERNAME and config.ES_PASSWORD:
            es_config['http_auth'] = (config.ES_USERNAME, config.ES_PASSWORD)
            
        # Add SSL configuration if enabled
        if config.ES_USE_SSL:
            es_config['use_ssl'] = True
            es_config['verify_certs'] = config.ES_VERIFY_CERTS
            if config.ES_CA_CERTS:
                es_config['ca_certs'] = config.ES_CA_CERTS
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Elasticsearch at {config.ES_HOST} (attempt {attempt+1}/{max_retries})")
                es = Elasticsearch(**es_config)
                if es.ping():
                    logger.info(f"Successfully connected to Elasticsearch")
                    return es
            except Exception as e:
                logger.warning(f"Elasticsearch connection attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to Elasticsearch after {max_retries} attempts")
                    raise
                time.sleep(retry_delay)
        
        return None
    
    def _create_consumer(self):
        """Create and configure Kafka consumer."""
        try:
            consumer = KafkaConsumer(
                config.LOGS_TOPIC,
                bootstrap_servers=[config.KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=f"{config.KAFKA_GROUP_ID_PREFIX}_correlation_group",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000  # 1 second timeout to check for termination
            )
            logger.info(f"Kafka consumer created successfully for topic {config.LOGS_TOPIC}")
            return consumer
        except Exception as e:
            logger.critical(f"Failed to create Kafka consumer: {e}")
            raise
    
    def _create_producer(self):
        """Create and configure Kafka producer."""
        try:
            producer = KafkaProducer(
                bootstrap_servers=[config.KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka producer created successfully")
            return producer
        except Exception as e:
            logger.critical(f"Failed to create Kafka producer: {e}")
            raise

    def reload_sigma_rules(self):
        """Load or reload Sigma rules from the rules directory."""
        global compiled_rules, sigma_rules_last_reload
        
        try:
            sigma_rules = load_sigma_rules(config.CORRELATION_RULES_DIR)
            new_compiled_rules = []
            
            for rule_dict in sigma_rules:
                try:
                    func = advanced_sigma_to_python_condition(rule_dict)
                    if func:
                        new_compiled_rules.append((rule_dict, func))
                        logger.debug(f"Compiled rule: {rule_dict.get('title')}")
                    else:
                        logger.warning(f"Could not compile rule: {rule_dict.get('title')}")
                except Exception as e:
                    logger.error(f"Error compiling rule '{rule_dict.get('title')}': {e}")
            
            logger.info(f"Loaded {len(new_compiled_rules)} sigma rules successfully")
            compiled_rules = new_compiled_rules
            sigma_rules_last_reload = time.time()
        except Exception as e:
            logger.error(f"Error reloading Sigma rules: {e}")
    
    def process_event(self, event):
        """Process a single event against all rules."""
        # Check if it's time to reload rules
        if time.time() - sigma_rules_last_reload > config.SIGMA_RULE_RELOAD_INTERVAL:
            logger.info("Reloading Sigma rules due to reload interval")
            self.reload_sigma_rules()
        
        # Process event against Sigma rules
        self._process_sigma_rules(event)
        
        # Process event for multi-step detection
        self._process_multi_step(event)
    
    def _process_sigma_rules(self, event):
        """Process event against all Sigma rules."""
        for rule_dict, check_func in compiled_rules:
            try:
                if check_func(event):
                    self._handle_sigma_rule_match(rule_dict, event)
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule_dict.get('title')}' against event: {e}")
    
    def _handle_sigma_rule_match(self, rule_dict, event):
        """Handle a match against a Sigma rule."""
        # Create a unique hash for the event + rule combination
        rule_id = rule_dict.get("id", "unknown")
        event_str = json.dumps(event, sort_keys=True)
        dedup_key = f"{rule_id}:{hash(event_str)}"
        
        # Check if we've already alerted on this exact event + rule
        if dedup_key in alert_deduplication:
            logger.debug(f"Duplicate alert suppressed for rule {rule_id}")
            return
        
        # Add to deduplication cache
        alert_deduplication.add(dedup_key)
        
        # Extract MITRE ATT&CK techniques and tags
        mitre_techniques = self._extract_mitre_tags(rule_dict)
        
        # Create alert document
        alert_doc = {
            "@timestamp": datetime.utcnow().isoformat() + 'Z',
            "alert_timestamp": time.time(),
            "alert_type": rule_dict.get("title", "Sigma-Alert"),
            "rule_id": rule_id,
            "description": rule_dict.get("description"),
            "level": rule_dict.get("level", "medium"),
            "log_data": event,
            "mitre_techniques": mitre_techniques,
            "tags": rule_dict.get("tags", [])
        }
        
        # Send to Kafka
        try:
            self.producer.send(config.ALERTS_TOPIC, alert_doc)
            logger.info(f"SIGMA ALERT sent to Kafka: {alert_doc['alert_type']} | Rule: {rule_id}")
        except Exception as e:
            logger.error(f"Failed to send SIGMA ALERT to Kafka: {e}")
        
        # Index in Elasticsearch
        try:
            res = self.es.index(index=config.ALERT_INDEX, document=alert_doc)
            logger.info(f"SIGMA ALERT Indexed: {alert_doc['alert_type']} | Rule: {rule_id} | ES ID: {res.get('_id')}")
        except Exception as e:
            logger.error(f"Failed to index SIGMA ALERT to Elasticsearch: {e}")
    
    def _process_multi_step(self, event):
        """Process event for multi-step attack patterns."""
        try:
            now = time.time()
            ip = event.get("ip", "unknown_ip")
            evt_type = event.get("event_type", "INFO")
            
            events_deque = ip_events[ip]
            
            # Remove old events outside the correlation window
            while events_deque and (now - events_deque[0][0]) >= config.CORRELATION_WINDOW_SECONDS:
                events_deque.popleft()
            
            # Add current event
            events_deque.append((now, evt_type))
            
            # Check for pattern matching
            if len(events_deque) >= 5:
                last_5_types = [et for ts, et in list(events_deque)[-5:]]
                
                if (last_5_types[0] in ["ERROR", "WARN"] and
                    last_5_types[1] in ["ERROR", "WARN"] and
                    last_5_types[2] in ["ERROR", "WARN"] and
                    last_5_types[3] == "INFO" and
                    last_5_types[4] == "PRIV"):
                    
                    # Create unique hash for deduplication
                    dedup_key = f"multi_step:{ip}:{now:.0f}"
                    
                    # Check for duplicate alerts in the deduplication window
                    if dedup_key not in alert_deduplication:
                        alert_deduplication.add(dedup_key)
                        self._handle_multi_step_match(event, ip)
        except Exception as e:
            logger.error(f"Error in multi-step processing: {e}")
    
    def _handle_multi_step_match(self, event, ip):
        """Handle a multi-step pattern match."""
        alert_doc = {
            "@timestamp": datetime.utcnow().isoformat() + 'Z',
            "alert_timestamp": time.time(),
            "alert_type": "Multi-step Attack",
            "description": "Detected pattern: fail->fail->fail->success->priv",
            "level": "high",
            "log_data": event,
            "ip": ip,
            "user": event.get("user"),
            "mitre_techniques": ["attack.t1078"],  # Valid Accounts
            "tags": ["multi_step", "authentication", "privilege_escalation"]
        }
        
        # Send to Kafka
        try:
            self.producer.send(config.ALERTS_TOPIC, alert_doc)
            logger.info(f"MULTI-STEP ALERT sent to Kafka for IP: {ip}")
        except Exception as e:
            logger.error(f"Failed to send MULTI-STEP ALERT to Kafka: {e}")
        
        # Index in Elasticsearch
        try:
            res = self.es.index(index=config.ALERT_INDEX, document=alert_doc)
            logger.info(f"MULTI-STEP ALERT Indexed for IP: {ip} | ES ID: {res.get('_id')}")
        except Exception as e:
            logger.error(f"Failed to index MULTI-STEP ALERT to Elasticsearch: {e}")
    
    def _extract_mitre_tags(self, rule_dict):
        """Extract MITRE ATT&CK technique IDs from rule tags."""
        tags = rule_dict.get("tags", [])
        mitre_tags = []
        
        for tag in tags:
            if isinstance(tag, str) and tag.startswith("attack.t"):
                mitre_tags.append(tag)
        
        return mitre_tags
    
    def _clear_deduplication_cache(self):
        """Periodically clear the deduplication cache to prevent memory leaks."""
        global alert_deduplication
        current_size = len(alert_deduplication)
        logger.debug(f"Clearing deduplication cache (size: {current_size})")
        alert_deduplication.clear()
        
        # Reschedule the timer
        self.dedup_cleaner = threading.Timer(300, self._clear_deduplication_cache)
        self.dedup_cleaner.daemon = True
        self.dedup_cleaner.start()
    
    def run(self):
        """Main processing loop."""
        logger.info("Correlation Engine started")
        
        try:
            while running:
                try:
                    # Process available messages with timeout
                    for message in self.consumer:
                        if not running:
                            break
                        
                        self.process_event(message.value)
                except Exception as e:
                    if running:  # Only log if not shutting down
                        logger.error(f"Error processing messages: {e}")
                        logger.debug(traceback.format_exc())
                        time.sleep(1)  # Avoid tight error loop
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        try:
            if self.consumer:
                self.consumer.close()
            if self.dedup_cleaner:
                self.dedup_cleaner.cancel()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        logger.info("Correlation Engine shutdown complete")


def signal_handler(sig, frame):
    """Handle termination signals."""
    global running
    logger.info(f"Received signal {sig}, shutting down...")
    running = False


def main():
    """Main entry point."""
    global running
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        logger.info("[CorrelationEngine] Starting up...")
        logger.info(f"Kafka Broker: {config.KAFKA_BROKER}")
        logger.info(f"Elasticsearch Host: {config.ES_HOST}")
        logger.info(f"Rules Directory: {config.CORRELATION_RULES_DIR}")
        
        engine = CorrelationEngine()
        engine.run()
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.debug(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
