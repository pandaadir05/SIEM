import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
LOGS_TOPIC = os.getenv("LOGS_TOPIC", "logs_raw")
ALERTS_TOPIC = os.getenv("ALERTS_TOPIC", "alerts")

# Elasticsearch Configuration
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
LOGS_INDEX = os.getenv("LOGS_INDEX", "logs")
ALERT_INDEX = os.getenv("ALERT_INDEX", "alerts")

# Backend API Configuration
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "supersecret-change-me")
API_PORT = int(os.getenv("API_PORT", 5000))
# Add JWT specific configs if implementing JWT
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")

# LLM Configuration
LLM_PORT = int(os.getenv("LLM_PORT", 7000))
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Example

# Correlation Engine
CORRELATION_RULES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "rules"))
CORRELATION_WINDOW_SECONDS = int(os.getenv("CORRELATION_WINDOW_SECONDS", 300))

# SOAR
SOAR_PLAYBOOK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "soar", "playbooks")) # Example path

# Add other configurations as needed
