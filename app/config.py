import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./greenhouse.db")
API_TOKEN = os.getenv("API_TOKEN", "")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN is required. Set it in .env")
