#!/usr/bin/env python3
import json
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
ALERTS_TOPIC = "alerts"

def main():
    consumer = KafkaConsumer(
        ALERTS_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("[AlertDispatcher] Listening for alerts...")

    for msg in consumer:
        alert = msg.value
        print("[AlertDispatcher] Received alert:", alert)
        # Integrate Slack, Email, etc.

if __name__ == "__main__":
    main()
