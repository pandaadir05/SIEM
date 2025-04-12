#!/usr/bin/env python3
import json
import time
import sys
import os
import signal
import threading
from datetime import datetime, timezone
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch, helpers, exceptions as es_exceptions
import logging
from logging.handlers import RotatingFileHandler
import traceback

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Set up logging
log_file = os.path.join(config.LOG_DIR, "indexer.log")
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if not config.DEBUG_MODE else logging.DEBUG)
logger.addHandler(handler)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# Global variables for metrics and control
running = True
stats = {
    "messages_processed": 0,
    "messages_failed": 0,
    "batches_indexed": 0,
    "batches_failed": 0,
    "start_time": time.time()
}

class ESIndexer:
    """Elasticsearch indexer that efficiently processes logs from Kafka."""
    
    def __init__(self):
        self.es_client = self._connect_elasticsearch()
        self._ensure_index_exists()
        self.message_buffer = []
        self.lock = threading.Lock()
        self.last_batch_time = time.time()
        
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
    
    def _ensure_index_exists(self):
        """Create the logs index if it doesn't exist."""
        try:
            if not self.es_client.indices.exists(index=config.LOGS_INDEX):
                logger.info(f"Creating index {config.LOGS_INDEX}")
                # Define a basic index mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "@timestamp": {"type": "date"},
                            "timestamp": {"type": "date"},
                            "event_type": {"type": "keyword"},
                            "user": {"type": "keyword"},
                            "ip": {"type": "ip"},
                            "message": {"type": "text"},
                            "CommandLine": {"type": "text"}
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
                self.es_client.indices.create(index=config.LOGS_INDEX, body=mapping)
                logger.info(f"Index {config.LOGS_INDEX} created successfully")
        except Exception as e:
            logger.warning(f"Error checking/creating index: {e}")
    
    def process_message(self, message):
        """Process a single message from Kafka."""
        try:
            # Handle both string and bytes messages
            if isinstance(message.value, bytes):
                raw_str = message.value.decode('utf-8')
            else:
                raw_str = message.value
                
            # Parse the JSON
            doc = json.loads(raw_str)
            
            # --- Timestamp Handling ---
            original_timestamp_float = doc.get('timestamp')
            
            if original_timestamp_float:
                # Ensure @timestamp is correctly formatted ISO 8601 UTC
                dt_object = datetime.fromtimestamp(original_timestamp_float, tz=timezone.utc)
                doc['@timestamp'] = dt_object.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                
                # Convert original 'timestamp' field to epoch milliseconds (integer)
                # This matches the default 'epoch_millis' format expected by ES date type
                doc['timestamp'] = int(original_timestamp_float * 1000)
            else:
                # Fallback if original timestamp is missing
                now_dt = datetime.now(timezone.utc)
                doc['@timestamp'] = now_dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                # Add timestamp in milliseconds if it was missing
                doc['timestamp'] = int(now_dt.timestamp() * 1000)
            # --- End Timestamp Handling ---

            with self.lock:
                self.message_buffer.append(doc)
                
            stats["messages_processed"] += 1
            
            # Check if it's time to flush the buffer
            self._check_flush_buffer()
            
            return True
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            stats["messages_failed"] += 1
            logger.warning(f"Skipping invalid message: {str(message.value)[:100]}... Error: {e}")
            return False
        except Exception as e:
            stats["messages_failed"] += 1
            logger.error(f"Error processing message: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def _check_flush_buffer(self):
        """Check if we should flush the buffer based on size or time."""
        with self.lock:
            now = time.time()
            buffer_size = len(self.message_buffer)
            
            if buffer_size >= config.ES_BULK_SIZE:
                logger.debug(f"Buffer full ({buffer_size} messages), indexing batch")
                self._flush_buffer()
            elif buffer_size > 0 and (now - self.last_batch_time) >= config.ES_BULK_TIMEOUT:
                logger.debug(f"Timeout reached, indexing {buffer_size} messages")
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush the message buffer to Elasticsearch."""
        with self.lock:
            if not self.message_buffer:
                return
            
            buffer_copy = self.message_buffer.copy()
            self.message_buffer = []
            self.last_batch_time = time.time()
        
        try:
            success_count = self._bulk_index(buffer_copy)
            if success_count:
                stats["batches_indexed"] += 1
                logger.info(f"Successfully indexed {success_count}/{len(buffer_copy)} documents")
            else:
                stats["batches_failed"] += 1
                logger.warning(f"Failed to index batch of {len(buffer_copy)} documents")
        except Exception as e:
            stats["batches_failed"] += 1
            logger.error(f"Error during bulk indexing: {e}")
            logger.debug(traceback.format_exc())
    
    def _bulk_index(self, documents, retry_count=3):
        """Index documents in bulk with retry logic."""
        if not documents:
            return 0
            
        actions = [
            {
                "_index": config.LOGS_INDEX,
                "_source": doc
            }
            for doc in documents
        ]
        
        for attempt in range(retry_count):
            try:
                success, failed = helpers.bulk(
                    self.es_client, 
                    actions, 
                    stats_only=True,
                    raise_on_error=False,
                    raise_on_exception=False,
                    max_retries=3,
                    initial_backoff=2,
                    max_backoff=60
                )
                
                if failed:
                    logger.warning(f"Bulk indexed with {failed} failures (attempt {attempt+1})")
                    if attempt == retry_count - 1:
                        logger.error(f"Failed to index {failed} documents after {retry_count} attempts")
                
                return success
            except es_exceptions.ConnectionError as e:
                logger.warning(f"Connection error during bulk indexing (attempt {attempt+1}): {e}")
                if attempt == retry_count - 1:
                    logger.error(f"Failed to connect to Elasticsearch after {retry_count} attempts")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error during bulk indexing: {e}")
                raise
                
        return 0
        
    def flush_remaining(self):
        """Flush any remaining messages in the buffer."""
        with self.lock:
            if self.message_buffer:
                logger.info(f"Flushing remaining {len(self.message_buffer)} messages")
                self._flush_buffer()


def signal_handler(sig, frame):
    """Handle termination signals gracefully."""
    global running
    logger.info("Received termination signal, shutting down...")
    running = False


def print_stats():
    """Print indexer statistics."""
    runtime = time.time() - stats["start_time"]
    rate = stats["messages_processed"] / runtime if runtime > 0 else 0
    
    logger.info("=== Indexer Statistics ===")
    logger.info(f"Runtime: {runtime:.2f} seconds")
    logger.info(f"Messages processed: {stats['messages_processed']}")
    logger.info(f"Messages failed: {stats['messages_failed']}")
    logger.info(f"Batches indexed: {stats['batches_indexed']}")
    logger.info(f"Batches failed: {stats['batches_failed']}")
    logger.info(f"Processing rate: {rate:.2f} messages/second")
    logger.info("=========================")


def main():
    """Main function to run the indexer."""
    logger.info("Starting Elasticsearch Indexer...")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            config.LOGS_TOPIC,
            bootstrap_servers=[config.KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=f"{config.KAFKA_GROUP_ID_PREFIX}_indexer_group",
            consumer_timeout_ms=config.KAFKA_CONSUMER_TIMEOUT_MS
        )
        
        # Create indexer
        indexer = ESIndexer()
        
        logger.info(f"Consuming from '{config.LOGS_TOPIC}', indexing to '{config.LOGS_INDEX}'...")
        
        # Process messages until termination
        while running:
            try:
                for message in consumer:
                    if not running:
                        break
                    indexer.process_message(message)
                
                # Check for timeout-based flush (consumer timeout expired)
                indexer._check_flush_buffer()
                
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                logger.debug(traceback.format_exc())
                time.sleep(5)  # Avoid tight error loop
        
        # Clean shutdown
        logger.info("Shutting down indexer...")
        indexer.flush_remaining()
        consumer.close()
        print_stats()
        logger.info("Indexer shutdown complete")
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.debug(traceback.format_exc())
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
