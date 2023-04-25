import sqlite3
from datetime import datetime


def init_conversations_db():
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY, user_id INTEGER, role TEXT, content TEXT, timestamp TEXT)"""
    )
    conn.commit()
    conn.close()


def init_token_db():
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS token_usage
                 (id INTEGER PRIMARY KEY, user_id INTEGER, timestamp TEXT, prompt_tokens INTEGER,
                 completion_tokens INTEGER, total_tokens INTEGER)"""
    )
    conn.commit()
    conn.close()


def init_db():
    init_conversations_db()
    init_token_db()


def add_message(user_id, role, content):
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO conversations (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, timestamp),
    )
    conn.commit()
    conn.close()


def get_conversation_history(user_id):
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM conversations WHERE user_id=? ORDER BY timestamp ASC", (user_id,))
    messages = [{"role": role, "content": content} for role, content in c.fetchall()]
    conn.close()
    return messages


def clear_conversation_history(user_id):
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def add_token_usage(user_id, prompt_tokens, completion_tokens, total_tokens):
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO token_usage (user_id, timestamp, prompt_tokens, completion_tokens, total_tokens) VALUES (?, ?, ?,"
        " ?, ?)",
        (user_id, timestamp, prompt_tokens, completion_tokens, total_tokens),
    )
    conn.commit()
    conn.close()


def get_total_tokens_used(user_id):
    conn = sqlite3.connect("conversation_history.db")
    c = conn.cursor()
    c.execute("SELECT SUM(total_tokens) FROM token_usage WHERE user_id=?", (user_id,))
    total_tokens = c.fetchone()[0]
    conn.close()
    return total_tokens if total_tokens else 0
