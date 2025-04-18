import sqlite3

def init_db():
    conn = sqlite3.connect("chexbot.db")
    c = conn.cursor()
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
