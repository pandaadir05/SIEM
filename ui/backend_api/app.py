#!/usr/bin/env python3
import json
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import logging
from prometheus_flask_exporter import PrometheusFlaskExporter

# Assuming config.py is accessible
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import config
# Import auth_required - RBAC needs significant rework for production
from rbac import auth_required, current_user

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = config.API_SECRET_KEY

# Add Prometheus metrics endpoint /metrics
metrics = PrometheusFlaskExporter(app)

# Initialize Elasticsearch client
try:
    es = Elasticsearch(config.ES_HOST)
    es.ping()
    logger.info(f"Connected to Elasticsearch at {config.ES_HOST}")
except Exception as e:
    logger.error(f"Failed to connect to Elasticsearch at {config.ES_HOST}: {e}", exc_info=True)
    es = None

# Common metric for endpoint calls
common_metric = metrics.counter(
    'api_calls_total', 'Total number of API calls',
    labels={'endpoint': lambda: request.endpoint}
)

@app.route("/api/health")
@metrics.do_not_track()
def health_check():
    es_status = "connected" if es and es.ping() else "disconnected"
    return jsonify({"status": "ok", "elasticsearch": es_status})

@app.route("/api/logs", methods=["GET"])
@auth_required
@common_metric
def get_logs():
    if not es:
        return jsonify({"error": "Elasticsearch not available"}), 503

    size = request.args.get('size', 50, type=int)
    page = request.args.get('page', 1, type=int)
    query_filter = request.args.get('q', None)

    es_from = (page - 1) * size

    body = {
        "size": size,
        "from": es_from,
        "sort": [{"@timestamp": {"order": "desc", "format": "strict_date_optional_time_nanos"}}],
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    if query_filter:
        body["query"]["bool"]["must"].append({
            "query_string": {
                "query": query_filter
            }
        })
    else:
        body["query"] = {"match_all": {}}

    try:
        resp = es.search(index=config.LOGS_INDEX, body=body)
        hits = resp["hits"]["hits"]
        total = resp["hits"]["total"]["value"]
        return jsonify({
            "logs": [h["_source"] for h in hits],
            "total": total,
            "page": page,
            "size": size
        })
    except Exception as e:
        logger.error(f"Error querying Elasticsearch for logs: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve logs"}), 500

@app.route("/api/alerts", methods=["GET"])
@auth_required
@common_metric
def get_alerts():
    if not es:
        return jsonify({"error": "Elasticsearch not available"}), 503

    size = request.args.get('size', 50, type=int)
    page = request.args.get('page', 1, type=int)
    query_filter = request.args.get('q', None)

    es_from = (page - 1) * size

    body = {
        "size": size,
        "from": es_from,
        "sort": [{"@timestamp": {"order": "desc", "format": "strict_date_optional_time_nanos"}}],
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    if query_filter:
        body["query"]["bool"]["must"].append({
            "query_string": {"query": query_filter}
        })
    else:
        body["query"] = {"match_all": {}}

    try:
        resp = es.search(index=config.ALERT_INDEX, body=body)
        hits = resp["hits"]["hits"]
        total = resp["hits"]["total"]["value"]
        return jsonify({
            "alerts": [h["_source"] for h in hits],
            "total": total,
            "page": page,
            "size": size
        })
    except Exception as e:
        logger.error(f"Error querying Elasticsearch for alerts: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve alerts"}), 500

@app.route("/api/alerts/<alert_id>", methods=["GET"])
@auth_required
@common_metric
def get_alert(alert_id):
    if not es:
        return jsonify({"error": "Elasticsearch not available"}), 503
    try:
        doc = es.get(index=config.ALERT_INDEX, id=alert_id)
        return jsonify(doc["_source"])
    except elasticsearch.NotFoundError:
        return jsonify({"error": "Alert not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve alert"}), 500

@app.route("/api/login", methods=["POST"])
@common_metric
def login():
    data = request.json
    user = data.get("user")
    pwd = data.get("password")
    if user == "admin" and pwd == "admin123":
        logger.info(f"Successful login attempt for user: {user} (using placeholder auth)")
        return jsonify({"token": "fake-jwt-token-admin"})
    else:
        logger.warning(f"Failed login attempt for user: {user}")
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    import elasticsearch
    logger.info(f"Starting Backend API on port {config.API_PORT}")
    app.run(host='0.0.0.0', port=config.API_PORT, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
