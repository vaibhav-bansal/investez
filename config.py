import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
CONVERSATIONS_DIR = BASE_DIR / "conversations"
CACHE_DIR = BASE_DIR / "cache"
FUNDAMENTALS_CACHE_DIR = CACHE_DIR / "fundamentals"

# Ensure directories exist
CONVERSATIONS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
FUNDAMENTALS_CACHE_DIR.mkdir(exist_ok=True)

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

# Cache settings
CACHE_TTL_HOURS = 24

# Screener.in settings
SCREENER_BASE_URL = "https://www.screener.in"
SCREENER_RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-20250514"
