#!/usr/bin/env python3
import json
import time
import os
from kafka import KafkaConsumer, KafkaProducer
from elasticsearch import Elasticsearch
import logging
from collections import defaultdict, deque
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from correlation.sigma_loader import load_sigma_rules
from correlation.sigma_translator import advanced_sigma_to_python_condition

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ip_events = defaultdict(lambda: deque(maxlen=10))

def process_multi_step(event):
    now = time.time()
    ip = event.get("ip", "unknown_ip")
    evt_type = event.get("event_type", "INFO")

    events_deque = ip_events[ip]

    while events_deque and (now - events_deque[0][0]) >= config.CORRELATION_WINDOW_SECONDS:
        events_deque.popleft()

    events_deque.append((now, evt_type))

    if len(events_deque) >= 5:
        last_5_types = [et for ts, et in list(events_deque)[-5:]]

        if (last_5_types[0] in ["ERROR", "WARN"] and
            last_5_types[1] in ["ERROR", "WARN"] and
            last_5_types[2] in ["ERROR", "WARN"] and
            last_5_types[3] == "INFO" and
            last_5_types[4] == "PRIV"):
            logger.info(f"Multi-step pattern matched for IP: {ip}")
            return True
    return False

def extract_mitre_tags(rule_dict):
    tags = rule_dict.get("tags", [])
    return [t for t in tags if t.startswith("attack.t")]

def main():
    logger.info("[CorrelationEngine] Starting up...")
    logger.info(f"Kafka Broker: {config.KAFKA_BROKER}")
    logger.info(f"Elasticsearch Host: {config.ES_HOST}")
    logger.info(f"Rules Directory: {config.CORRELATION_RULES_DIR}")

    sigma_rules = load_sigma_rules(config.CORRELATION_RULES_DIR)
    compiled_rules = []
    for rd in sigma_rules:
        func = advanced_sigma_to_python_condition(rd)
        if func:
            compiled_rules.append((rd, func))
            logger.debug(f"Compiled rule: {rd.get('title')}")
        else:
            logger.warning(f"Could not compile rule: {rd.get('title')}")

    consumer = KafkaConsumer(
        config.LOGS_TOPIC,
        bootstrap_servers=[config.KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='siem_correlation_group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=[config.KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    es = Elasticsearch(config.ES_HOST)

    logger.info(f"[CorrelationEngine] {len(compiled_rules)} sigma rules loaded. Listening on {config.LOGS_TOPIC}...")

    for msg in consumer:
        try:
            event = msg.value
            if not isinstance(event, dict):
                logger.warning(f"Received non-dict message: {event}")
                continue

            event_timestamp = event.get('timestamp', time.time())

            for (rule_dict, check_func) in compiled_rules:
                try:
                    if check_func(event):
                        mitre = extract_mitre_tags(rule_dict)
                        alert_doc = {
                            "@timestamp": datetime.utcnow().isoformat() + 'Z',
                            "alert_timestamp": time.time(),
                            "alert_type": rule_dict.get("title", "Sigma-Alert"),
                            "rule_id": rule_dict.get("id"),
                            "description": rule_dict.get("description"),
                            "level": rule_dict.get("level", "medium"),
                            "log_data": event,
                            "mitre_techniques": mitre,
                            "tags": rule_dict.get("tags", [])
                        }
                        producer.send(config.ALERTS_TOPIC, alert_doc)
                        es.index(index=config.ALERT_INDEX, document=alert_doc)
                        logger.info(f"SIGMA ALERT: {alert_doc['alert_type']} | Rule: {alert_doc['rule_id']} | MITRE: {mitre}")
                except Exception as rule_exc:
                    logger.error(f"Error evaluating rule '{rule_dict.get('title')}': {rule_exc}", exc_info=True)

            try:
                if process_multi_step(event):
                    alert_doc = {
                        "@timestamp": datetime.utcnow().isoformat() + 'Z',
                        "alert_timestamp": time.time(),
                        "alert_type": "Multi-step Attack",
                        "description": "Detected pattern: fail->fail->fail->success->priv",
                        "level": "high",
                        "log_data": event,
                        "ip": event.get("ip"),
                        "user": event.get("user")
                    }
                    producer.send(config.ALERTS_TOPIC, alert_doc)
                    es.index(index=config.ALERT_INDEX, document=alert_doc)
                    logger.info(f"MULTI-STEP ALERT triggered for IP: {event.get('ip')}!")
            except Exception as multi_step_exc:
                logger.error(f"Error during multi-step processing: {multi_step_exc}", exc_info=True)

        except json.JSONDecodeError:
            logger.warning(f"Failed to decode Kafka message value: {msg.value[:100]}...")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

if __name__ == "__main__":
    main()
