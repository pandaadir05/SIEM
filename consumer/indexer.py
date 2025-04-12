#!/usr/bin/env python3
import json
import time
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch, helpers
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # Number of messages to batch before sending to ES
BATCH_TIMEOUT_SECONDS = 5  # Max time to wait before sending a partial batch

def bulk_indexer(es_client, buffer):
    """ Sends documents to Elasticsearch using the bulk helper """
    actions = [
        {
            "_index": config.LOGS_INDEX,
            "_source": doc
        }
        for doc in buffer
    ]
    try:
        success, failed = helpers.bulk(es_client, actions, raise_on_error=False, raise_on_exception=False)
        logger.info(f"Bulk indexed: {success} success, {failed} failures")
        if failed:
            logger.error(f"Failed bulk operations: {failed}")
        return success
    except Exception as e:
        logger.error(f"Error during bulk indexing: {e}", exc_info=True)
        return 0

def main():
    logger.info("Starting Indexer...")
    logger.info(f"Kafka Broker: {config.KAFKA_BROKER}")
    logger.info(f"Elasticsearch Host: {config.ES_HOST}")
    logger.info(f"Consuming from topic: {config.LOGS_TOPIC}")
    logger.info(f"Indexing to index: {config.LOGS_INDEX}")

    consumer = KafkaConsumer(
        config.LOGS_TOPIC,
        bootstrap_servers=[config.KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='siem_indexer_group',
        consumer_timeout_ms=BATCH_TIMEOUT_SECONDS * 1000
    )
    es = Elasticsearch(config.ES_HOST)

    message_buffer = []
    last_batch_time = time.time()

    logger.info(f"Consuming from '{config.LOGS_TOPIC}', indexing to '{config.LOGS_INDEX}'...")

    while True:
        try:
            for msg in consumer:
                try:
                    raw_str = msg.value.decode('utf-8')
                    doc = json.loads(raw_str)
                    if '@timestamp' not in doc:
                        doc['@timestamp'] = datetime.utcfromtimestamp(doc.get('timestamp', time.time())).isoformat() + 'Z'
                    message_buffer.append(doc)
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    logger.warning(f"Skipping invalid message: {msg.value[:100]}... Error: {e}")
                    continue

                if len(message_buffer) >= BATCH_SIZE:
                    logger.info(f"Buffer full ({len(message_buffer)} messages), indexing batch...")
                    bulk_indexer(es, message_buffer)
                    message_buffer.clear()
                    last_batch_time = time.time()

            if message_buffer:
                now = time.time()
                if now - last_batch_time >= BATCH_TIMEOUT_SECONDS:
                    logger.info(f"Timeout reached or consumer finished, indexing remaining {len(message_buffer)} messages...")
                    bulk_indexer(es, message_buffer)
                    message_buffer.clear()
                    last_batch_time = now

        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
