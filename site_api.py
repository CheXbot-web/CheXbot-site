import requests
from config import SITE_API_URL, UPDATE_API_KEY

def post_cache_update(claim_id, result):
    headers = {
        "Authorization": f"Bearer {UPDATE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "claim_id": claim_id,
        "result": result
    }

    response = requests.post(SITE_API_URL, headers=headers, json=data, timeout=60)

    if response.status_code == 200:
        print(f"✅ Pushed claim {claim_id} to site")
        return True
    else:
        print(f"⚠️ Site update failed ({response.status_code}): {response.text}")
        return False

