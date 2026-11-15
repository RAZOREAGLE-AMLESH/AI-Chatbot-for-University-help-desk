"""
models/conversation.py — Conversation & Message Table Definitions
AI Chatbot for University Help Desk | KIET Group of Institutions

Tables:
    conversation  — one record per chat session
    message       — one record per individual message (user or bot)

Relationships:
    conversation 1 ——< message  (one conversation has many messages)
    message.conversation_id references conversation.id  (FK with CASCADE DELETE)
"""

import sqlite3
from datetime import datetime, timezone
from models import get_connection


# ──────────────────────────────────────────────
# DDL — Table creation SQL
# ──────────────────────────────────────────────

CREATE_CONVERSATION_TABLE = """
CREATE TABLE IF NOT EXISTS conversation (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL
);
"""

CREATE_MESSAGE_TABLE = """
CREATE TABLE IF NOT EXISTS message (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender          TEXT    NOT NULL CHECK(sender IN ('user', 'bot')),
    message         TEXT    NOT NULL,
    confidence      REAL,
    timestamp       TEXT    NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE
);
"""


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row) if row else None


# ──────────────────────────────────────────────
# Conversation Operations
# ──────────────────────────────────────────────

def get_or_create_conversation(session_id: str, db_path: str = None) -> dict:
    """
    Return the conversation for the given session_id.
    Creates a new one if it does not exist yet.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM conversation WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row:
            return row_to_dict(row)
        now = _now()
        cursor = conn.execute(
            "INSERT INTO conversation (session_id, created_at) VALUES (?, ?)",
            (session_id, now)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM conversation WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_conversation_by_session(session_id: str, db_path: str = None) -> dict | None:
    """Return a conversation record by session_id or None."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM conversation WHERE session_id = ?", (session_id,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


# ──────────────────────────────────────────────
# Message Operations
# ──────────────────────────────────────────────

def save_message(conversation_id: int, sender: str, message: str,
                 confidence: float = None, db_path: str = None) -> dict:
    """
    Persist a single chat message.

    Args:
        conversation_id: FK to the conversation table.
        sender: Either 'user' or 'bot'.
        message: The message text.
        confidence: Optional confidence score (only relevant for bot messages).
    """
    conn = get_connection(db_path)
    now = _now()
    try:
        cursor = conn.execute(
            """INSERT INTO message (conversation_id, sender, message, confidence, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (conversation_id, sender, message, confidence, now)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM message WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_messages_for_session(session_id: str, limit: int = 20,
                              db_path: str = None) -> list[dict]:
    """
    Return the most recent messages for a given session, oldest first.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """SELECT m.* FROM message m
               JOIN conversation c ON c.id = m.conversation_id
               WHERE c.session_id = ?
               ORDER BY m.id DESC
               LIMIT ?""",
            (session_id, limit)
        ).fetchall()
        return list(reversed([row_to_dict(r) for r in rows]))
    finally:
        conn.close()


def count_conversations(db_path: str = None) -> int:
    """Return total number of conversations."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM conversation").fetchone()
        return row["cnt"]
    finally:
        conn.close()


def count_messages(db_path: str = None) -> int:
    """Return total number of messages."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM message").fetchone()
        return row["cnt"]
    finally:
        conn.close()
