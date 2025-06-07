import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ===== APP CONFIGURATION =====
APP_DEBUG = os.environ.get("APP_DEBUG", "True").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
API_TITLE = os.environ.get("API_TITLE", "Cookie Compliance Analyzer")
API_DESCRIPTION = os.environ.get("API_DESCRIPTION")
API_VERSION = os.environ.get("API_VERSION", "1.0.0")
API_BASE = os.environ.get("API_BASE")

# ===== DATABASE CONFIGURATION =====
DB_NAME = os.environ.get("DB_NAME")
USERS_COLLECTION = os.environ.get("USERS_COLLECTION", "users")
ROLE_CHANGE_REQUESTS_COLLECTION = os.environ.get("ROLE_CHANGE_REQUESTS_COLLECTION", "role_change_requests")

POLICY_DISCOVERY_COLLECTION = os.environ.get("POLICY_DISCOVERY_COLLECTION", "policy_discoveries")
POLICY_CONTENTS_COLLECTION = os.environ.get("POLICY_CONTENTS_COLLECTION", "policy_contents")
COOKIE_FEATURES_COLLECTION = os.environ.get("COOKIE_FEATURES_COLLECTION", "cookie_features")
VIOLATIONS_COLLECTION = os.environ.get("VIOLATIONS_COLLECTION", "cookie_violations")

MONGODB_PWD = os.environ.get("MONGODB_PWD")
MONGODB_USER = os.environ.get("MONGODB_USER", "username")
MONGODB_CLUSTER = os.environ.get("MONGODB_CLUSTER", "cluster.mongodb.net")

# ===== EXTERNAL SERVICES =====
HF_TOKEN = os.environ.get("HF_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NGROK_AUTHTOKEN = os.environ.get("NGROK_AUTHTOKEN")

# ===== HELPER FUNCTIONS =====
def get_mongodb_uri() -> str:
    """Generate MongoDB connection URI"""
    if not all([MONGODB_PWD, DB_NAME, MONGODB_USER]):
        raise ValueError("Missing required MongoDB environment variables")
    return f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@{MONGODB_CLUSTER}/{DB_NAME}"

def validate_required_configs():
    """Validate required environment variables"""
    required_vars = {
        'DB_NAME': DB_NAME,
        'MONGODB_PWD': MONGODB_PWD,
        'MONGODB_CLUSTER': MONGODB_CLUSTER
    }

    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
