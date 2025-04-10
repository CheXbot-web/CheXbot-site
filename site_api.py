import requests
import json
from config import UPDATE_API_KEY, SITE_API_URL

def post_cache_update(claim_id, data):
    try:
        response = requests.post(
            SITE_API_URL,
            headers={"Authorization": f"Bearer {UPDATE_API_KEY}"},
            json={"claim_id": claim_id, "data": data},
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Cache update posted to site for {claim_id}")
        else:
            if "text/html" in response.headers.get("Content-Type", ""):
                print(f"⚠️ Site update failed with HTML content ({response.status_code})")
            else:
                print(f"⚠️ Site update failed ({response.status_code}): {response.text[:300]}")

    except Exception as e:
        print(f"❌ Error posting to site: {e}")
