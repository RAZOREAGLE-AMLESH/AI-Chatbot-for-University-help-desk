"""
services/chatbot_service.py — Core Chatbot Orchestration
AI Chatbot for University Help Desk | KIET Group of Institutions

Responsibilities:
    1. Load FAQs from the database and build the TF-IDF index.
    2. Accept a user query, compute similarity, and return the best answer.
    3. Apply a confidence threshold — refuse to invent information.
    4. Persist every exchange to the conversation log.
    5. Expose an index-rebuild function for use after FAQ updates.

Confidence threshold:
    If the best cosine-similarity score is below CONFIDENCE_THRESHOLD, the
    chatbot returns a transparent fallback message rather than a low-quality
    answer. This prevents the bot from fabricating KIET-specific details.
"""

import uuid
from services.nlp_service import get_engine, rebuild_index
from services.database_service import (
    list_faqs, record_exchange
)


# ──────────────────────────────────────────────
# Tuneable constants
# ──────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.20   # Minimum cosine similarity to return an answer
TOP_K = 5                      # Number of candidates evaluated per query

FALLBACK_RESPONSE = (
    "I'm sorry, I couldn't find a verified answer to your question in my "
    "knowledge base. For accurate information, please:\n"
    "• Visit the official KIET website: https://www.kiet.edu/\n"
    "• Contact the KIET help desk directly.\n"
    "• Email: info@kiet.edu"
)

FALLBACK_CATEGORY = "Unknown"
FALLBACK_SOURCE = "https://www.kiet.edu/"


# ──────────────────────────────────────────────
# In-memory FAQ cache & Question Variations
# ──────────────────────────────────────────────

QUESTION_VARIATIONS_BY_TEXT: dict[str, list[str]] = {
    "what is kiet group of institutions?": [
        "What is KIET?",
        "Tell me about KIET",
        "About KIET",
        "Information about KIET",
        "Introduce KIET",
    ],
    "what b.tech programmes does kiet offer?": [
        "What courses are offered at KIET?",
        "What courses does KIET offer?",
        "Which courses are available in KIET?",
        "What branches are offered at KIET?",
        "B.Tech branches in KIET",
        "List of programmes offered at KIET",
        "Courses available at KIET",
    ],
    "what is the contact number for kiet?": [
        "How can I contact KIET?",
        "KIET contact details",
        "KIET phone number",
        "KIET helpline number",
    ],
    "where can i find information about kiet fee structure?": [
        "What is the fee structure?",
        "What is the fees of KIET?",
        "KIET college fees",
        "Fee structure for KIET",
    ],
    "how do i contact the kiet help desk?": [
        "How can I contact KIET?",
        "KIET help desk",
    ],
    "how do i check my exam results?": [
        "How do I check my examination results?",
        "How can I check my KIET semester results?",
        "Where can I see my exam results?",
        "How to download my KIET result?",
        "How do I download my grade sheet?",
        "Download semester grade sheet",
        "KIET semester results",
        "KIET exam result portal",
    ],
}

_faq_cache: list[dict] = []
_index_to_faq_map: list[int] = []


def _load_and_index(db_path: str = None) -> None:
    """
    Fetch all FAQs from the database, cache them, and (re)build the TF-IDF index.
    Called once at startup and whenever FAQs are modified.
    Supports question variations for each FAQ.
    """
    global _faq_cache, _index_to_faq_map
    _faq_cache = list_faqs(db_path=db_path)

    corpus: list[str] = []
    _index_to_faq_map = []

    for faq_idx, faq in enumerate(_faq_cache):
        q_text = faq["question"].strip()
        corpus.append(q_text)
        _index_to_faq_map.append(faq_idx)

        # Include question variations if defined
        variations = QUESTION_VARIATIONS_BY_TEXT.get(q_text.lower(), [])
        for var in variations:
            corpus.append(var)
            _index_to_faq_map.append(faq_idx)

    rebuild_index(corpus)


def refresh_index(db_path: str = None) -> None:
    """Public API — call this after adding/editing/deleting FAQs."""
    _load_and_index(db_path)


# ──────────────────────────────────────────────
# Main chat handler
# ──────────────────────────────────────────────

def get_answer(user_message: str, session_id: str = None,
               db_path: str = None) -> dict:
    """
    Process a user message and return a structured response.

    Args:
        user_message: Raw text from the user (already validated by the route).
        session_id:   Optional session identifier. A new UUID is generated if
                      not provided.
        db_path:      Optional DB path override (used in tests).

    Returns:
        {
            "success":    bool,
            "answer":     str,
            "category":   str,
            "source":     str | None,
            "confidence": float,         # actual cosine-similarity score
            "session_id": str
        }
    """
    # Ensure session_id exists
    if not session_id:
        session_id = str(uuid.uuid4())

    # Lazily load the index on first call or if the cache is empty
    engine = get_engine()
    if not engine.is_fitted or engine.corpus_size == 0:
        _load_and_index(db_path)
        engine = get_engine()

    # Edge case: knowledge base is empty
    if engine.corpus_size == 0:
        response = {
            "success": True,
            "answer": (
                "The knowledge base is currently empty. Please ask an admin "
                "to populate it with KIET FAQ data."
            ),
            "category": FALLBACK_CATEGORY,
            "source": FALLBACK_SOURCE,
            "confidence": 0.0,
            "session_id": session_id,
        }
        record_exchange(session_id, user_message, response["answer"],
                        response["confidence"], db_path)
        return response

    # Retrieve top candidates across corpus and aggregate by FAQ
    candidates = engine.query(user_message, k=TOP_K * 4)

    faq_scores: dict[int, float] = {}
    for corpus_idx, score in candidates:
        if corpus_idx < len(_index_to_faq_map):
            faq_idx = _index_to_faq_map[corpus_idx]
            if faq_idx not in faq_scores or score > faq_scores[faq_idx]:
                faq_scores[faq_idx] = score

    sorted_faqs = sorted(faq_scores.items(), key=lambda x: x[1], reverse=True)
    best_index, best_score = sorted_faqs[0] if sorted_faqs else (None, 0.0)
    best_score = round(best_score, 4)

    if best_score >= CONFIDENCE_THRESHOLD and best_index is not None and best_index < len(_faq_cache):
        matched_faq = _faq_cache[best_index]
        answer = matched_faq["answer"]
        category = matched_faq["category"]
        source = matched_faq.get("source_url") or FALLBACK_SOURCE
        is_verified = bool(matched_faq.get("is_verified", 0))
    else:
        answer = FALLBACK_RESPONSE
        category = FALLBACK_CATEGORY
        source = FALLBACK_SOURCE
        is_verified = False

    response = {
        "success": True,
        "answer": answer,
        "category": category,
        "source": source,
        "is_verified": is_verified,
        "confidence": best_score,
        "session_id": session_id,
    }

    # Persist the exchange
    record_exchange(session_id, user_message, answer, best_score, db_path)

    return response


def initialise_chatbot(db_path: str = None) -> int:
    """
    Load FAQs and build the TF-IDF index.
    Call this from the Flask app factory during startup.

    Returns:
        Number of FAQs indexed.
    """
    _load_and_index(db_path)
    return get_engine().corpus_size
