#!/usr/bin/env python3
import json
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

# JWT Authentication
def create_token(user_id, role):
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {'user_id': user_id, 'role': role, 'exp': expiration},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
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
            token = create_token(username, 'admin')
            return jsonify({"token": token})
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Authentication failed"}), 500

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv('API_PORT', config.API_PORT))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Backend API on port {port}")
    app.run(
        host='127.0.0.1',  # Only bind to localhost
        port=port,
        debug=debug
    )
