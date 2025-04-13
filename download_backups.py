import requests
import datetime

BASE_URL = "https://chexbot-web.onrender.com/backup"
FILES = ["chexbot.db", "last_seen.json"]
DEST_FOLDER = "backups"

def download(file):
    url = f"{BASE_URL}/{file}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    dest = f"{DEST_FOLDER}/{timestamp}_{file}"

    response = requests.get(url)
    if response.status_code == 200:
        with open(dest, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded: {dest}")
    else:
        print(f"❌ Failed to download {file}: {response.status_code}")

if __name__ == "__main__":
    import os
    os.makedirs(DEST_FOLDER, exist_ok=True)
    for f in FILES:
        download(f)
