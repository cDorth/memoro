import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'memoro.db')

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            summary TEXT,
            timestamp TEXT,
            tags TEXT,
            embedding BLOB
        )
    ''')
    conn.commit()
    conn.close()