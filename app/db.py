from datetime import datetime
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'memoro.db')

def save_note(content, summary, tags, embedding=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''
        INSERT INTO notes (content, summary, timestamp, tags, embedding)
        VALUES (?, ?, ?, ?, ?)
    ''', (content, summary, timestamp, ','.join(tags), embedding))
    conn.commit()
    conn.close()
