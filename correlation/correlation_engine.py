#!/usr/bin/env python3
import json
import time
import os
from kafka import KafkaConsumer, KafkaProducer
from elasticsearch import Elasticsearch

from correlation.sigma_loader import load_sigma_rules
from correlation.sigma_translator import advanced_sigma_to_python_condition

KAFKA_BROKER = "localhost:9092"
LOGS_TOPIC = "logs_raw"
ALERTS_TOPIC = "alerts"
ES_HOST = "http://localhost:9200"
ALERT_INDEX = "alerts"

CURRENT_DIR = os.path.dirname(__file__)
RULES_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "rules"))

# multi-step memory
WINDOW_SECONDS = 300
ip_events = {}

def process_multi_step(event):
    now = time.time()
    ip = event.get("ip","unknown_ip")
    evt_type = event.get("event_type","INFO")

    if ip not in ip_events:
        ip_events[ip] = []
    # remove old
    ip_events[ip] = [(ts,et) for (ts,et) in ip_events[ip] if (now - ts) < WINDOW_SECONDS]

    ip_events[ip].append((now, evt_type))

    # if last 5 = fail,fail,fail,success,priv
    last_events = [et for (_,et) in ip_events[ip][-5:]]
    if len(last_events) == 5:
        if (last_events[0] in ["ERROR","WARN"] and
            last_events[1] in ["ERROR","WARN"] and
            last_events[2] in ["ERROR","WARN"] and
            last_events[3] == "INFO" and
            last_events[4] == "PRIV"):
            return True
    return False

def extract_mitre_tags(rule_dict):
    tags = rule_dict.get("tags",[])
    return [t for t in tags if t.startswith("attack.t")]

def main():
    print("[CorrelationEngine] Starting up...")

    # load sigma
    sigma_rules = load_sigma_rules(RULES_DIR)
    compiled_rules = []
    for rd in sigma_rules:
        func = advanced_sigma_to_python_condition(rd)
        if func:
            compiled_rules.append((rd, func))

    consumer = KafkaConsumer(
        LOGS_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    es = Elasticsearch(ES_HOST)

    print(f"[CorrelationEngine] {len(compiled_rules)} sigma rules loaded. Listening on {LOGS_TOPIC}...")

    for msg in consumer:
        event = msg.value

        # A) Sigma detection
        for (rule_dict, check_func) in compiled_rules:
            if check_func(event):
                mitre = extract_mitre_tags(rule_dict)
                alert_doc = {
                    "timestamp": time.time(),
                    "alert_type": rule_dict.get("title","Sigma-Alert"),
                    "rule_id": rule_dict.get("id"),
                    "description": rule_dict.get("description"),
                    "level": rule_dict.get("level","medium"),
                    "log_data": event,
                    "mitre_techniques": mitre
                }
                producer.send(ALERTS_TOPIC, alert_doc)
                es.index(index=ALERT_INDEX, body=alert_doc)
                print("[CorrelationEngine] SIGMA ALERT:", alert_doc["alert_type"], "| MITRE=", mitre)

        # B) multi-step
        if process_multi_step(event):
            alert_doc = {
                "timestamp": time.time(),
                "alert_type": "Multi-step Attack",
                "description": "fail->fail->fail->success->priv",
                "level": "high",
                "log_data": event
            }
            producer.send(ALERTS_TOPIC, alert_doc)
            es.index(index=ALERT_INDEX, body=alert_doc)
            print("[CorrelationEngine] MULTI-STEP ALERT triggered!")

if __name__ == "__main__":
    main()
