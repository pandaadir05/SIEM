#!/usr/bin/env python3
import json
import time  # Added import
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch, NotFoundError
import logging
from prometheus_flask_exporter import PrometheusMetrics
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    import config
except ImportError as e:
    logger.error(f"Failed to load config: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('API_SECRET_KEY', config.API_SECRET_KEY)
CORS(app)

# Add Prometheus metrics
metrics = PrometheusMetrics(app)
common_metric = metrics.counter(
    'api_calls_total',
    'Total number of API calls',
    labels={'endpoint': lambda: request.endpoint}
)

# Initialize Elasticsearch client with retry
def init_elasticsearch(max_retries=3, retry_delay=5):
    es_host = os.getenv('ES_HOST', config.ES_HOST)
    for attempt in range(max_retries):
        try:
            es = Elasticsearch(es_host)
            if es.ping():
                logger.info(f"Connected to Elasticsearch at {es_host}")
                return es
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to Elasticsearch after {max_retries} attempts: {e}")
                return None
            logger.warning(f"Elasticsearch connection attempt {attempt + 1} failed, retrying...")
            time.sleep(retry_delay)
    return None

es = init_elasticsearch()

# JWT Authentication (Decorator modified for temporary hardcoded token)
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        # --- Temporary Hardcoded Token Check ---
        if token == "fake-jwt-token-admin":
            request.current_user = {"user_id": "admin", "role": "admin"}
            logger.debug("Auth successful via temporary hardcoded token.")
            return f(*args, **kwargs)
        # --- End Temporary Check ---

        logger.warning(f"Auth failed: Invalid or missing token. Header: '{auth_header[:30]}...'")
        return jsonify({'error': 'Unauthorized', 'message': 'Valid Bearer token required'}), 401

    return decorated

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route("/api/health")
@metrics.counter('healthcheck_requests', 'Number of healthcheck requests')
def health():
    try:
        if es and es.ping():
            return jsonify({"status": "healthy", "elasticsearch": "connected"})
        return jsonify({"status": "degraded", "elasticsearch": "disconnected"}), 503
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
@common_metric
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get("user")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        # TODO: Replace with proper authentication
        if username == "admin" and password == "admin123":
            token = jwt.encode(
                {'user_id': username, 'role': 'admin', 'exp': datetime.utcnow() + timedelta(hours=24)},
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({"token": token})
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Authentication failed"}), 500

@app.route("/api/stats")
@auth_required
@common_metric
def get_stats():
    """ Provides basic stats like total alerts and critical alerts. """
    if not es:
        return jsonify({"error": "Elasticsearch not available"}), 503

    try:
        # Count total alerts
        total_resp = es.count(index=config.ALERT_INDEX, body={"query": {"match_all": {}}})
        total_alerts = total_resp.get('count', 0)

        # Count critical alerts (adjust level field/values as needed)
        critical_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"level": "high"}},
                        {"match": {"level": "critical"}}
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        critical_resp = es.count(index=config.ALERT_INDEX, body=critical_query)
        critical_alerts = critical_resp.get('count', 0)

        stats = {
            "totalAlerts": total_alerts,
            "criticalAlerts": critical_alerts,
        }
        return jsonify(stats)

    except NotFoundError:
        logger.warning(f"Stats endpoint: Index '{config.ALERT_INDEX}' not found.")
        return jsonify({"totalAlerts": 0, "criticalAlerts": 0})
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch statistics"}), 500

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv('API_PORT', config.API_PORT))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Backend API on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
