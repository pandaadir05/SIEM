#!/usr/bin/env python3
import time
import json
import numpy as np
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

ES_HOST = "http://localhost:9200"
LOGS_INDEX = "logs"
ALERT_INDEX = "alerts"

def main():
    es = Elasticsearch(ES_HOST)
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    body = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": yesterday.timestamp() * 1000,
                    "lte": now.timestamp() * 1000,
                    "format": "epoch_millis"
                }
            }
        },
        "size": 10000
    }
    resp = es.search(index=LOGS_INDEX, body=body)
    hits = resp["hits"]["hits"]
    print(f"[AnomalyDetector] Fetched {len(hits)} logs from last 24h")

    hours = []
    for h in hits:
        doc = h["_source"]
        ts = doc.get("timestamp")
        if ts:
            dt = datetime.utcfromtimestamp(ts)
            hours.append(dt.hour)

    if len(hours) < 10:
        print("[AnomalyDetector] Not enough data to analyze.")
        return

    arr = np.array(hours)
    mean = np.mean(arr)
    std = np.std(arr)
    print(f"[AnomalyDetector] mean hour={mean:.2f}, std={std:.2f}")

    anomalies = []
    for h in hits:
        doc = h["_source"]
        ts = doc.get("timestamp")
        if ts:
            hr = datetime.utcfromtimestamp(ts).hour
            if abs(hr - mean) > 2 * std:
                anomalies.append(doc)

    for a in anomalies:
        alert_doc = {
            "timestamp": time.time(),
            "alert_type": "Anomalous Hour",
            "description": "Activity outside normal hours",
            "log_data": a
        }
        es.index(index=ALERT_INDEX, body=alert_doc)
        print("[AnomalyDetector] ALERT inserted:", alert_doc)

if __name__ == "__main__":
    main()
