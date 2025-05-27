from datetime import datetime
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'memoro.db')

def save_note(content, summary, tags, embedding=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    embedding_str = json.dumps(embedding) if embedding and isinstance(embedding, list) and len(embedding) == 384 else None
    c.execute('''
        INSERT INTO notes (content, summary, timestamp, tags, embedding)
        VALUES (?, ?, ?, ?, ?)
    ''', (content, summary, timestamp, ','.join(tags), embedding_str))
    conn.commit()
    conn.close()


def get_all_embeddings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, embedding FROM notes WHERE embedding IS NOT NULL")
    data = [(row[0], json.loads(row[1])) for row in c.fetchall()]
    conn.close()
    return data

def adicionar_coluna_embedding():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE notes ADD COLUMN embedding TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise
    conn.close()


def ensure_embedding_column_exists():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE notes ADD COLUMN embedding TEXT")
        conn.commit()
        print("✅ Coluna 'embedding' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ A coluna 'embedding' já existe.")
        else:
            raise
    finally:
        conn.close()

def get_notes_grouped_by_day():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, summary, tags, timestamp FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    grouped = {}
    for note in rows:
        date = note[3][:10]  # yyyy-mm-dd
        grouped.setdefault(date, []).append(note)
    return grouped

def init_db():
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            summary TEXT,
            tags TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_coluna_embedding():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE notes ADD COLUMN embedding TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise
    conn.close()



def get_all_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, summary, tags, timestamp FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_note_by_id(note_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, summary, tags, timestamp FROM notes WHERE id=?", (note_id,))
    note = c.fetchone()
    conn.close()
    return note

def update_note(note_id: int, new_content: str, new_summary: str, new_tags: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE notes SET content = ?, summary = ?, tags = ? WHERE id = ?",
              (new_content, new_summary, new_tags, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()