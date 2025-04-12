#!/usr/bin/env python3
import json
import time  # Added import
from flask import Flask, request, jsonify, g
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

# Load configuration and adjust sys.path
try:
    import sys
    # Add the SIEM root directory to sys.path so absolute imports work
    siem_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if siem_root_dir not in sys.path:
        sys.path.insert(0, siem_root_dir) # Insert at beginning to prioritize
    import config
except ImportError as e:
    logger.error(f"Failed to load config or modify sys.path: {e}")
    sys.exit(1)

# Now import rbac using absolute path, after sys.path is modified
try:
    from ui.backend_api.rbac import validate_jwt, AuthError, get_token_from_request
except ImportError as e:
    logger.error(f"Failed to import rbac after modifying sys.path: {e}")
    logger.error(f"Current sys.path: {sys.path}")
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

# --- Authentication Decorator ---
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_from_request()
            payload = validate_jwt(token)
            # Store user info in Flask's g object for access within the request
            g.current_user = payload 
            logger.debug(f"Auth successful for user: {payload.get('sub')}")
            return f(*args, **kwargs)
        except AuthError as e:
            logger.warning(f"Auth failed: {e.error}")
            return jsonify(e.error), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return jsonify({"error": "Internal server error during authentication"}), 500
            
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
    """Provide a simple login API for testing."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    username = data.get("user")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # For testing purposes - use hardcoded credentials
    valid_credentials = {
        "admin": "admin123",
        "analyst": "analyst123",
        "viewer": "viewer123"
    }
    
    if username in valid_credentials and password == valid_credentials[username]:
        # Determine role based on username
        role = "admin" if username == "admin" else "analyst" if username == "analyst" else "viewer"
        
        # Generate a JWT token (simple version for testing)
        payload = {
            "sub": username,
            "role": role,
            "exp": int(time.time()) + 3600  # 1 hour expiry
        }
        token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
        
        # Return token and user data
        return jsonify({
            "token": token,
            "user": {
                "username": username,
                "role": role
            }
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/verify-token", methods=["GET"])
@auth_required  # Use the decorator to ensure a valid token is present
def verify_token():
    """Verify the provided JWT token and return user information"""
    # If @auth_required passes, g.current_user should be set
    user_info = g.current_user
    if not user_info:
         # This case should ideally be caught by @auth_required
         logger.error("User info not found in g after auth_required passed.")
         return jsonify({"error": "Authentication check failed unexpectedly"}), 500
         
    # Return user data from token payload stored in g
    return jsonify({
        "username": user_info.get("sub"),
        "role": user_info.get("role")
    })

@app.route("/api/stats", methods=["GET"])
@auth_required  # Apply the decorator here as well
def get_stats():
    """Get dashboard statistics"""
    # Access user info if needed: user = g.current_user
    logger.info(f"Stats requested by user: {g.current_user.get('sub')}")
    try:
        # Example hardcoded stats for demo purposes
        return jsonify({
            "total_alerts": 42,
            "critical_alerts": 5,
            "events_today": 1250,
            "systems_monitored": 18
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": "Failed to get statistics"}), 500

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
