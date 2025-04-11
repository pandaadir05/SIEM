#!/usr/bin/env python3
import json
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

from rbac import auth_required, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret"

es = Elasticsearch("http://localhost:9200")

@app.route("/api/logs", methods=["GET"])
@auth_required
def get_logs():
    body = {"size": 50, "sort":[{"timestamp":{"order":"desc"}}]}
    resp = es.search(index="logs", body=body)
    hits = resp["hits"]["hits"]
    return jsonify([h["_source"] for h in hits])

@app.route("/api/alerts", methods=["GET"])
@auth_required
def get_alerts():
    body = {"size": 50, "sort":[{"timestamp":{"order":"desc"}}]}
    resp = es.search(index="alerts", body=body)
    hits = resp["hits"]["hits"]
    return jsonify([h["_source"] for h in hits])

@app.route("/api/alerts/<alert_id>", methods=["GET"])
@auth_required
def get_alert(alert_id):
    try:
        doc = es.get(index="alerts", id=alert_id)
        return doc["_source"]
    except:
        return jsonify({"error": "Not found"}), 404

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("user")
    pwd = data.get("password")
    if user == "admin" and pwd == "admin123":
        # Fake token
        return jsonify({"token":"fake-jwt-token-admin"})
    else:
        return jsonify({"error":"Invalid credentials"}),401

if __name__ == "__main__":
    app.run(port=5000, debug=True)
