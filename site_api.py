import requests
# from config import SITE_API_URL, UPDATE_API_KEY
import threading
SITE_API_URL = "https://chexbot-web.onrender.com/update"
UPDATE_API_KEY = "jB5jdm44haN4txs4lULsPYYizgekrahniu" 
def trust_level_emoji(confidence):
    if confidence >= 0.90:
        return "🟩", "5/5"
    elif confidence >= 0.75:
        return "🟨", "4/5"
    elif confidence >= 0.60:
        return "🟧", "3/5"
    elif confidence >= 0.40:
        return "🟥", "2/5"
    else:
        return "⬛", "1/5"

def random_catchphrase():
    import random
    phrases = [
        "Truth is trending.",
        "Verified by CheXbot.",
        "Facts over fiction.",
        "Reality check complete.",
        "Stay informed."
    ]
    return random.choice(phrases)


def post_cache_update(claim_id, result):
    def send_update():
        try:
            headers = {
                "Authorization": f"Bearer {UPDATE_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {"claim_id": claim_id, "result": result}
            response = requests.post(SITE_API_URL, headers=headers, json=data, timeout=200)

            if response.status_code == 200:
                print(f"✅ Pushed claim {claim_id} to site")
            else:
                print(f"⚠️ Site update failed ({response.status_code}): {response.text}")

        except Exception as e:
            print(f"❌ Error posting to site: {e}")

    # Launch update in a new thread (non-blocking)
    threading.Thread(target=send_update, daemon=True).start()
