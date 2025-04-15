import requests
import zipfile
import io
import os
import shutil

BACKUP_URL = "https://chexbot-web.onrender.com/backup"
OUTPUT_DIR = "./backup"
FRESH_COPY = os.path.join(OUTPUT_DIR, "chexbot.db")
ARCHIVE_COPY = os.path.join(OUTPUT_DIR, "chexbot_archive.db")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_and_extract_backup():
    try:
        print("📡 Requesting backup from site...")
        response = requests.get(BACKUP_URL, timeout=60)
        response.raise_for_status()

        print("📦 Backup ZIP downloaded. Extracting...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)

        if os.path.exists(FRESH_COPY):
            print("✅ chexbot.db extracted successfully.")

            # Optionally archive the last version (you can comment this out if manual)
            shutil.copy(FRESH_COPY, ARCHIVE_COPY)
            print("📂 Archive updated:", ARCHIVE_COPY)

        else:
            print("⚠️ chexbot.db not found after extraction!")

    except Exception as e:
        print("❌ Failed to download or extract backup:", e)

if __name__ == "__main__":
    download_and_extract_backup()
