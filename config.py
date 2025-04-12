import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load .env file if it exists (for local development)
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    logger.info(f"Loading environment from {env_file}")
    load_dotenv(env_file)
else:
    logger.info("No .env file found, using environment variables or defaults")

# Helper function to get environment variables with validation
def get_env(key, default=None, required=False, validator=None):
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    if validator and value is not None:
        try:
            return validator(value)
        except Exception as e:
            raise ValueError(f"Invalid value for {key}: {e}")
    return value

# Kafka Configuration
KAFKA_BROKER = get_env("KAFKA_BROKER", "localhost:9092")
LOGS_TOPIC = get_env("LOGS_TOPIC", "logs_raw")
ALERTS_TOPIC = get_env("ALERTS_TOPIC", "alerts")
KAFKA_GROUP_ID_PREFIX = get_env("KAFKA_GROUP_ID_PREFIX", "siem")
KAFKA_CONSUMER_TIMEOUT_MS = get_env("KAFKA_CONSUMER_TIMEOUT_MS", 5000, validator=int)

# Elasticsearch Configuration
ES_HOST = get_env("ES_HOST", "http://localhost:9200")
ES_USERNAME = get_env("ES_USERNAME", None)
ES_PASSWORD = get_env("ES_PASSWORD", None)
ES_USE_SSL = get_env("ES_USE_SSL", "false", validator=lambda x: x.lower() == "true")
ES_VERIFY_CERTS = get_env("ES_VERIFY_CERTS", "true", validator=lambda x: x.lower() == "true")
ES_CA_CERTS = get_env("ES_CA_CERTS", None)
LOGS_INDEX = get_env("LOGS_INDEX", "logs")
ALERT_INDEX = get_env("ALERT_INDEX", "alerts")
ES_BULK_SIZE = get_env("ES_BULK_SIZE", 100, validator=int)
ES_BULK_TIMEOUT = get_env("ES_BULK_TIMEOUT", 5, validator=int)

# Backend API Configuration
API_SECRET_KEY = get_env("API_SECRET_KEY", "supersecret-change-me")
API_PORT = get_env("API_PORT", 5000, validator=int)
JWT_SECRET_KEY = get_env("JWT_SECRET_KEY", API_SECRET_KEY)  # Default to API_SECRET_KEY if not set
JWT_ACCESS_TOKEN_EXPIRES = get_env("JWT_ACCESS_TOKEN_EXPIRES", 3600, validator=int)  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = get_env("JWT_REFRESH_TOKEN_EXPIRES", 86400 * 30, validator=int)  # 30 days

# LLM Configuration
LLM_PORT = get_env("LLM_PORT", 7000, validator=int)
LLM_MODEL = get_env("LLM_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = get_env("OPENAI_API_KEY")

# Correlation Engine
CORRELATION_RULES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "rules"))
CORRELATION_WINDOW_SECONDS = get_env("CORRELATION_WINDOW_SECONDS", 300, validator=int)
SIGMA_RULE_RELOAD_INTERVAL = get_env("SIGMA_RULE_RELOAD_INTERVAL", 60, validator=int)  # seconds

# SOAR
SOAR_PLAYBOOK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "soar", "playbooks"))
SOAR_ENABLED = get_env("SOAR_ENABLED", "false", validator=lambda x: x.lower() == "true")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Features
ENABLE_RATE_LIMITING = get_env("ENABLE_RATE_LIMITING", "false", validator=lambda x: x.lower() == "true")
RATE_LIMIT_DEFAULT = get_env("RATE_LIMIT_DEFAULT", "100/hour")
DEBUG_MODE = get_env("DEBUG_MODE", "false", validator=lambda x: x.lower() == "true")

# Print configuration summary
logger.info("=== SIEM Configuration ===")
logger.info(f"Kafka Broker: {KAFKA_BROKER}")
logger.info(f"Elasticsearch Host: {ES_HOST}")
logger.info(f"Debug Mode: {DEBUG_MODE}")
logger.info(f"Rules Directory: {CORRELATION_RULES_DIR}")
logger.info("==========================")
