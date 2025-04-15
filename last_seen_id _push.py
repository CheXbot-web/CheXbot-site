import sqlite3

DB_FILE = "chexbot.db"
NEW_LAST_SEEN_ID = "1912345678901234567"  # <- Replace with your desired tweet ID

def update_last_seen(db_path, tweet_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure the metadata table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Insert or update the last_seen_id
    cursor.execute('''
        INSERT INTO metadata (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    ''', ("last_seen_id", str(tweet_id)))

    conn.commit()
    conn.close()
    print(f"✅ Updated last_seen_id to {tweet_id}")

update_last_seen(DB_FILE, NEW_LAST_SEEN_ID)
