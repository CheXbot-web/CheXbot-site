# db.py
import sqlite3

DB_FILE = "chexbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Example: your existing table(s)
    c.execute('''
        CREATE TABLE IF NOT EXISTS fact_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_tweet_id TEXT,
            reply_id TEXT,
            username TEXT,
            claim TEXT,
            verdict TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_metadata():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_metadata(key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM metadata WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_metadata(key, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO metadata (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def save_fact_check(original_tweet_id, reply_id, username, claim, verdict, confidence):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO fact_checks (original_tweet_id, chexbot_reply_id, username, claim, verdict, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (original_tweet_id, reply_id, username, claim, verdict, confidence))
    conn.commit()
    conn.close()

def get_fact_check_by_reply_id(reply_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM fact_checks WHERE chexbot_reply_id = ?', (reply_id,))
    row = c.fetchone()
    conn.close()
    return row

__all__ = ["init_db", "save_fact_check", "get_fact_check_by_reply_id", "get_metadata", "set_metadata","init_metadata"]
