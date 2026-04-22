import sqlite3
from contextlib import contextmanager
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_PATH = os.environ.get("DATABASE_PATH")

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    tags TEXT, --JSON array stored as string
                    payload TEXT,
                    UNIQUE(user_id, occurred_at)
                )
    """)
    conn.commit()
    conn.close()
    

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()