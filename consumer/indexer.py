#!/usr/bin/env python3
import json
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "logs_raw"
ES_HOST = "http://localhost:9200"
ES_INDEX = "logs"

def main():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    es = Elasticsearch(ES_HOST)

    print(f"[Indexer] Consuming from '{TOPIC_NAME}', indexing to '{ES_INDEX}'...")

    for msg in consumer:
        try:
            raw_str = msg.value.decode('utf-8')
            doc = json.loads(raw_str)
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("[Indexer] Skipping invalid message:", msg.value)
            continue

        # Use 'document' instead of 'body' to avoid deprecation
        es.index(index=ES_INDEX, document=doc)
        # show raw_log or entire doc
        print("[Indexer] Indexed doc:", doc.get("raw_log", "(no raw_log)"))

if __name__ == "__main__":
    main()
