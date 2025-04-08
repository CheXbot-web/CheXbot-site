# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect("chexbot.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS fact_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_tweet_id TEXT,
            chexbot_reply_id TEXT,
            username TEXT,
            claim TEXT,
            verdict TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_fact_check(original_tweet_id, reply_id, username, claim, verdict, confidence):
    conn = sqlite3.connect("chexbot.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO fact_checks (original_tweet_id, chexbot_reply_id, username, claim, verdict, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (original_tweet_id, reply_id, username, claim, verdict, confidence))
    conn.commit()
    conn.close()

def get_fact_check_by_reply_id(reply_id):
    conn = sqlite3.connect("chexbot.db")
    c = conn.cursor()
    c.execute('SELECT * FROM fact_checks WHERE chexbot_reply_id = ?', (reply_id,))
    row = c.fetchone()
    conn.close()
    return row
