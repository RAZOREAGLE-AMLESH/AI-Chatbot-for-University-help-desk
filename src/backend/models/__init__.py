"""
models/__init__.py — Database Initialization
AI Chatbot for University Help Desk | KIET Group of Institutions

Uses Python's built-in sqlite3 module (no external ORM required).
Provides a lightweight database abstraction layer.
"""

import sqlite3
import os
from datetime import datetime


# ──────────────────────────────────────────────
# Database path resolution
# ──────────────────────────────────────────────

def get_db_path() -> str:
    """Return the absolute path to the SQLite database file.

    Layout:
        sdp_project/
            src/backend/models/__init__.py   <- this file
            instance/chatbot.db              <- DB lives here
    """
    # models/ -> backend/ -> src/ -> sdp_project/
    models_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(models_dir)
    src_dir = os.path.dirname(backend_dir)
    project_root = os.path.dirname(src_dir)
    instance_dir = os.path.join(project_root, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    return os.path.join(instance_dir, "chatbot.db")


# Allow override via environment variable (useful for testing)
def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Return a sqlite3 connection with row_factory set to sqlite3.Row
    so rows can be accessed by column name.
    """
    path = db_path or os.environ.get("DATABASE_PATH") or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str = None) -> None:
    """
    Create all tables if they do not already exist.
    Safe to call on every startup.
    """
    from models.faq import CREATE_FAQ_TABLE
    from models.conversation import CREATE_CONVERSATION_TABLE, CREATE_MESSAGE_TABLE

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(f"""
            {CREATE_FAQ_TABLE}
            {CREATE_CONVERSATION_TABLE}
            {CREATE_MESSAGE_TABLE}
        """)
        conn.commit()
    finally:
        conn.close()
