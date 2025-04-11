#!/usr/bin/env python3
import os
import json
from kafka import KafkaConsumer
# import requests or other libs if you call external APIs

KAFKA_BROKER = "localhost:9092"
ALERTS_TOPIC = "alerts"

def run_playbook(alert):
    # example: if alert_type == "Suspicious Command Prompt", isolate host
    pass

def main():
    consumer = KafkaConsumer(
        ALERTS_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("[SOAR] Orchestrator is running...")

    for msg in consumer:
        alert = msg.value
        print("[SOAR] Got alert:", alert)
        # run playbook logic
        run_playbook(alert)

if __name__ == "__main__":
    main()
