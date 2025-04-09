# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Twitter (X) API keys
BEARER_TOKEN = os.getenv("bearer_token")
CONSUMER_KEY = os.getenv("consumer_key")
CONSUMER_SECRET = os.getenv("consumer_secret")
ACCESS_TOKEN = os.getenv("access_token")
ACCESS_SECRET = os.getenv("access_secret")

# Bitly
BITLY_TOKEN = os.getenv("bitly_token")

# OpenAI
OPENAI_KEY = os.getenv("openai_key")

# Google APIs
GOOGLE_API_KEY = os.getenv("google_api_key")
GOOGLE_CSE_ID = os.getenv("google_cse_id")

# === Optional: Feature Flags ===
USE_GPT = True
USE_BING = True
CONFIDENCE_THRESHOLD = 0.85

# Shared API Key between bot and site for /update endpoint
UPDATE_API_KEY = os.getenv("update_api_key")  # You can change this to anything strong

# Public Render URL of your Flask app
SITE_API_URL = "https://chexbot-web.onrender.com/update"
