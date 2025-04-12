#!/usr/bin/env python3
from kafka import KafkaConsumer, TopicPartition
import json

def list_kafka_topics():
    consumer = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest'
    )
    
    # Get all topics
    topics = consumer.topics()
    print("Available Kafka topics:", topics)
    
    # Check logs topic
    if 'logs_raw' in topics:
        tp = TopicPartition('logs_raw', 0)
        # Assign to partition
        consumer.assign([tp])
        # Seek to beginning
        consumer.seek_to_beginning(tp)
        
        # Get last offset
        end_offset = consumer.end_offsets([tp])
        print(f"logs_raw topic has approximately {end_offset[tp]} messages")
        
        # Read a few messages to check
        print("\nSample messages:")
        count = 0
        for message in consumer:
            if count >= 3:  # Just show 3 messages
                break
            try:
                value = json.loads(message.value.decode('utf-8'))
                print(f"Message {count}: {value}")
            except:
                print(f"Message {count}: {message.value}")
            count += 1
    else:
        print("logs_raw topic not found!")

if __name__ == "__main__":
    list_kafka_topics()
