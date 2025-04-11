#!/usr/bin/env python3
import time
import json
import os
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "logs_raw"
LOG_FILE = os.path.join("test_logs", "sample.log")

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    offset = 0
    print(f"[Agent] Tailing {LOG_FILE}. Ctrl+C to stop.")

    while True:
        if not os.path.exists(LOG_FILE):
            time.sleep(1)
            continue
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            f.seek(offset)
            new_data = f.read()
            offset = f.tell()

        lines = new_data.strip().split("\n")
        for line in lines:
            if line:
                event = {
                    "timestamp": time.time(),
                    "raw_log": line
                }
                producer.send(TOPIC_NAME, event)
                print(f"[Agent] Sent: {line}")
        time.sleep(1)

if __name__ == "__main__":
    main()
