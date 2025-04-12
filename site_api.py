import requests
from config import SITE_API_URL, UPDATE_API_KEY
import threading

def post_cache_update(claim_id, result):
    def send_update():
        try:
            headers = {
                "Authorization": f"Bearer {UPDATE_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {"claim_id": claim_id, "result": result}
            response = requests.post(SITE_API_URL, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                print(f"✅ Pushed claim {claim_id} to site")
            else:
                print(f"⚠️ Site update failed ({response.status_code}): {response.text}")

        except Exception as e:
            print(f"❌ Error posting to site: {e}")

    # Launch update in a new thread (non-blocking)
    threading.Thread(target=send_update, daemon=True).start()
