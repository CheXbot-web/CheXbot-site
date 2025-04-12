# test.py
import requests

SITE_API_URL = "https://chexbot-web.onrender.com/update"
UPDATE_API_KEY = "jB5jdm44haN4txs4lULsPYYizgekrahniu" # Replace this with the real key

data = {
    "claim_id": "test_ping",
    "result": {
        "verdict": "True",
        "confidence": 1.0
    }
}

headers = {
    "Authorization": f"Bearer {UPDATE_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(SITE_API_URL, json=data, headers=headers, timeout=150)
    print("✅ Status:", response.status_code)
    print("✅ Response:", response.text)
except Exception as e:
    print("❌ Error:", e)
