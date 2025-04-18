# db.py
import sqlite3
from datetime import datetime

DB_FILE = "chexbot.db"

def get_db_connection_dict():
    """Returns a connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection_tuple():
    """Returns a standard SQLite connection (tuple-style rows)."""
    return sqlite3.connect(DB_FILE)


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
        INSERT INTO fact_checks (original_tweet_id, reply_id, username, claim, verdict, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (original_tweet_id, reply_id, username, claim, verdict, confidence))
    conn.commit()
    conn.close()

def get_fact_check_by_reply_id(reply_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM fact_checks WHERE reply_id = ?', (reply_id,))
    row = c.fetchone()
    conn.close()
    return row


def init_claim_details():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS claim_details (
            claim_id TEXT PRIMARY KEY,
            gpt_summary TEXT,
            sources TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_claim_details(claim_id):
    conn = get_db_connection_dict()
    c = conn.cursor()
    c.execute('SELECT gpt_summary, sources FROM claim_details WHERE claim_id = ?', (claim_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_claim_details(claim_id, summary, sources=None):
    import json
    from datetime import datetime

    sources_json = json.dumps(sources or [])

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO claim_details (claim_id, gpt_summary, sources, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(claim_id) DO UPDATE SET
            gpt_summary=excluded.gpt_summary,
            sources=excluded.sources,
            updated_at=CURRENT_TIMESTAMP
    ''', (claim_id, summary, sources_json, datetime.now()))
    conn.commit()
    conn.close()

def get_fact_check_by_original_id(original_tweet_id):
    conn = get_db_connection_dict()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM fact_checks WHERE original_tweet_id = ?', (original_tweet_id,))
    row = c.fetchone()
    conn.close()
    return row


__all__ = ["init_db", "save_fact_check", "get_fact_check_by_reply_id", "get_metadata", "set_metadata","init_metadata","get_claim_details","init_claim_details","save_claim_details","get_fact_check_by_original_id"]
