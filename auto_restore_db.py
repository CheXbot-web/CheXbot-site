import requests
import zipfile
import io
import os
import shutil
from datetime import datetime

# === Config ===
BACKUP_URL = "https://chexbot-web.onrender.com/backup"
DOWNLOAD_PATH = "chexbot_backup.zip"
DB_DEST = "chexbot.db"
ARCHIVE_DIR = "db_archives"

# === Ensure archive directory exists ===
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# === Download and extract backup ===
print("📡 Downloading backup from server...")
try:
    response = requests.get(BACKUP_URL, timeout=120)
    response.raise_for_status()
    
    with open(DOWNLOAD_PATH, "wb") as f:
        f.write(response.content)
    print("✅ Backup downloaded successfully")

    # Archive current DB if it exists
    if os.path.exists(DB_DEST):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(ARCHIVE_DIR, f"chexbot_{timestamp}.db")
        shutil.copy2(DB_DEST, archive_path)
        print(f"📦 Existing DB archived to {archive_path}")

    # Extract the downloaded zip file
    with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
        zip_ref.extractall()
        print("✅ Backup extracted")

    os.remove(DOWNLOAD_PATH)
    print("🧹 Temporary zip file removed")

except requests.exceptions.RequestException as e:
    print(f"❌ Network error: {e}")
except zipfile.BadZipFile:
    print("❌ Failed to extract backup: Bad zip file")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

