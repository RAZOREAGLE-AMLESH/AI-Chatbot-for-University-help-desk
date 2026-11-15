"""
models/faq.py — FAQ Table Definition & Operations
AI Chatbot for University Help Desk | KIET Group of Institutions

Table: faq
Columns:
    id            INTEGER  PRIMARY KEY AUTOINCREMENT
    question      TEXT     NOT NULL
    answer        TEXT     NOT NULL
    category      TEXT     NOT NULL  (e.g. Admissions, Academics, Fees, Facilities)
    source_url    TEXT               (official KIET page URL)
    is_verified   INTEGER  DEFAULT 0 (1 = verified from official source)
    last_verified TEXT               (ISO date string)
    created_at    TEXT     NOT NULL
    updated_at    TEXT     NOT NULL
"""

import sqlite3
from datetime import datetime, timezone
from models import get_connection


# ──────────────────────────────────────────────
# DDL — Table creation SQL
# ──────────────────────────────────────────────

CREATE_FAQ_TABLE = """
CREATE TABLE IF NOT EXISTS faq (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    question      TEXT    NOT NULL,
    answer        TEXT    NOT NULL,
    category      TEXT    NOT NULL DEFAULT 'General',
    source_url    TEXT,
    is_verified   INTEGER NOT NULL DEFAULT 0,
    last_verified TEXT,
    created_at    TEXT    NOT NULL,
    updated_at    TEXT    NOT NULL
);
"""


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dictionary."""
    return dict(row) if row else None


# ──────────────────────────────────────────────
# CRUD Operations
# ──────────────────────────────────────────────

def get_all_faqs(db_path: str = None) -> list[dict]:
    """Return all FAQs ordered by category then id."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM faq ORDER BY category, id"
        ).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_faq_by_id(faq_id: int, db_path: str = None) -> dict | None:
    """Return a single FAQ by its primary key."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM faq WHERE id = ?", (faq_id,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def get_faqs_by_category(category: str, db_path: str = None) -> list[dict]:
    """Return all FAQs in a given category."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM faq WHERE LOWER(category) = LOWER(?) ORDER BY id",
            (category,)
        ).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def search_faqs(query: str, db_path: str = None) -> list[dict]:
    """
    Simple keyword search across question, answer and category.
    Returns rows where any of these columns contain the query substring.
    """
    conn = get_connection(db_path)
    like = f"%{query}%"
    try:
        rows = conn.execute(
            """SELECT * FROM faq
               WHERE question LIKE ? OR answer LIKE ? OR category LIKE ?
               ORDER BY category, id""",
            (like, like, like)
        ).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()


def create_faq(question: str, answer: str, category: str,
               source_url: str = None, is_verified: int = 0,
               last_verified: str = None, db_path: str = None) -> dict:
    """Insert a new FAQ and return the created record."""
    now = _now()
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """INSERT INTO faq (question, answer, category, source_url,
                                is_verified, last_verified, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (question.strip(), answer.strip(), category.strip(),
             source_url, is_verified, last_verified, now, now)
        )
        conn.commit()
        return get_faq_by_id(cursor.lastrowid, db_path)
    finally:
        conn.close()


def update_faq(faq_id: int, updates: dict, db_path: str = None) -> dict | None:
    """
    Update allowed fields of an existing FAQ.
    Only updates fields present in the `updates` dict.
    Returns the updated record or None if not found.
    """
    allowed = {"question", "answer", "category", "source_url",
                "is_verified", "last_verified"}
    fields = {k: v for k, v in updates.items() if k in allowed}

    if not fields:
        return get_faq_by_id(faq_id, db_path)

    fields["updated_at"] = _now()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [faq_id]

    conn = get_connection(db_path)
    try:
        conn.execute(f"UPDATE faq SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return get_faq_by_id(faq_id, db_path)
    finally:
        conn.close()


def delete_faq(faq_id: int, db_path: str = None) -> bool:
    """Delete a FAQ by id. Returns True if a row was deleted, False otherwise."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("DELETE FROM faq WHERE id = ?", (faq_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def count_faqs(db_path: str = None) -> int:
    """Return total number of FAQ records."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM faq").fetchone()
        return row["cnt"]
    finally:
        conn.close()
