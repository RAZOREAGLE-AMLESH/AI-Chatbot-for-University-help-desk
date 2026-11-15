"""
services/database_service.py — High-Level Database Operations
AI Chatbot for University Help Desk | KIET Group of Institutions

Thin service layer that wraps model-level functions and provides
higher-level operations consumed by the route handlers.
"""

import os
from models.faq import (
    get_all_faqs, get_faq_by_id, get_faqs_by_category,
    search_faqs, create_faq, update_faq, delete_faq, count_faqs
)
from models.conversation import (
    get_or_create_conversation, get_messages_for_session,
    save_message, count_conversations, count_messages
)


# ──────────────────────────────────────────────
# FAQ service helpers
# ──────────────────────────────────────────────

def list_faqs(category: str = None, db_path: str = None) -> list[dict]:
    """Return all FAQs, optionally filtered by category."""
    if category:
        return get_faqs_by_category(category, db_path)
    return get_all_faqs(db_path)


def find_faq(faq_id: int, db_path: str = None) -> dict | None:
    """Return a single FAQ or None."""
    return get_faq_by_id(faq_id, db_path)


def find_faqs_by_keyword(query: str, db_path: str = None) -> list[dict]:
    """Keyword search across question, answer, and category."""
    return search_faqs(query.strip(), db_path)


def add_faq(question: str, answer: str, category: str,
            source_url: str = None, is_verified: int = 0,
            last_verified: str = None, db_path: str = None) -> dict:
    """Create and return a new FAQ record."""
    return create_faq(
        question=question,
        answer=answer,
        category=category,
        source_url=source_url,
        is_verified=is_verified,
        last_verified=last_verified,
        db_path=db_path
    )


def edit_faq(faq_id: int, updates: dict, db_path: str = None) -> dict | None:
    """Update a FAQ and return the updated record, or None if not found."""
    existing = get_faq_by_id(faq_id, db_path)
    if not existing:
        return None
    return update_faq(faq_id, updates, db_path)


def remove_faq(faq_id: int, db_path: str = None) -> bool:
    """Delete a FAQ. Returns True on success, False if not found."""
    return delete_faq(faq_id, db_path)


def faq_count(db_path: str = None) -> int:
    return count_faqs(db_path)


# ──────────────────────────────────────────────
# Conversation & message helpers
# ──────────────────────────────────────────────

def record_exchange(session_id: str, user_message: str,
                    bot_response: str, confidence: float,
                    db_path: str = None) -> None:
    """
    Persist a full user↔bot exchange to the database.

    1. Get or create the conversation for this session.
    2. Save the user message.
    3. Save the bot response (with confidence score).
    """
    conv = get_or_create_conversation(session_id, db_path)
    conv_id = conv["id"]
    save_message(conv_id, "user", user_message, db_path=db_path)
    save_message(conv_id, "bot", bot_response, confidence=confidence, db_path=db_path)


def get_chat_history(session_id: str, limit: int = 20,
                     db_path: str = None) -> list[dict]:
    """Return the last `limit` messages for a session."""
    return get_messages_for_session(session_id, limit, db_path)


# ──────────────────────────────────────────────
# Stats
# ──────────────────────────────────────────────

def get_stats(db_path: str = None) -> dict:
    """Return aggregate statistics for the admin dashboard."""
    return {
        "total_faqs": count_faqs(db_path),
        "total_conversations": count_conversations(db_path),
        "total_messages": count_messages(db_path),
    }
