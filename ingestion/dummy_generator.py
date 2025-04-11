#!/usr/bin/env python3
import time
import json
import random
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "logs_raw"

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    event_types = ["INFO", "WARN", "ERROR", "PRIV"]
    while True:
        doc = {
            "timestamp": time.time(),
            "user": random.choice(["alice","bob","admin","guest"]),
            "event_type": random.choice(event_types),
            "ip": f"192.168.1.{random.randint(1,254)}",
            "CommandLine": random.choice([
                "C:\\Windows\\System32\\cmd.exe",
                "C:\\Windows\\System32\\powershell.exe",
                "/usr/bin/bash",
                "/usr/bin/python3"
            ]),
            "message": "some random log line"
        }
        producer.send(TOPIC_NAME, doc)
        print("[DummyGen] Sent:", doc)
        time.sleep(2)

if __name__ == "__main__":
    main()
