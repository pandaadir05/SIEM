#!/usr/bin/env python3
import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kafka import KafkaProducer

LOG_FILE_PATH = os.path.join("test_logs", "sample.log")
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "logs_raw"

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, producer, topic):
        self.file_path = file_path
        self.producer = producer
        self.topic = topic
        # track current file size to read new lines
        self.offset = os.path.getsize(file_path)

    def on_modified(self, event):
        """Called when the file changes."""
        if event.src_path.endswith(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                f.seek(self.offset)
                new_data = f.read()
                self.offset = f.tell()

            lines = new_data.strip().split("\n")
            for line in lines:
                if line:
                    event_dict = {
                        "timestamp": time.time(),
                        "log": line,
                        "source": self.file_path
                    }
                    self.producer.send(self.topic, event_dict)
                    print(f"[Tail] Sent log to Kafka: {line}")

def main():
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    event_handler = LogFileHandler(LOG_FILE_PATH, producer, TOPIC_NAME)
    observer = Observer()
    observer.schedule(event_handler, path="test_logs", recursive=False)

    print(f"[Tail] Monitoring {LOG_FILE_PATH} in real time...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
