import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./greenhouse.db")
API_TOKEN = os.getenv("API_TOKEN", "")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN is required. Set it in .env")

# CORS Configuration
# In production, set CORS_ORIGINS in .env as comma-separated list:
# CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
# For development, use "*" to allow all origins
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS_ENV == "*":
    CORS_ORIGINS: List[str] = ["*"]
else:
    # Split comma-separated origins and strip whitespace
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",") if origin.strip()]

# Rate Limiting Configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Request Size Limits (in bytes, default 1MB)
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", str(1024 * 1024)))  # 1MB default
