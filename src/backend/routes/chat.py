"""
routes/chat.py — Chat API Endpoint
AI Chatbot for University Help Desk | KIET Group of Institutions

POST /api/chat
    Request  : { "message": "...", "session_id": "..." (optional) }
    Response : { "success": true, "answer": "...", "category": "...",
                 "source": "...", "confidence": 0.85, "session_id": "..." }
"""

import os
from flask import Blueprint, request, jsonify
from services.chatbot_service import get_answer
from utils.validators import validate_chat_input

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Accept a user message and return the best matching FAQ answer.

    Error responses:
        400 — missing / invalid body, empty message, message too long
        415 — wrong Content-Type
        500 — unexpected server error
    """
    # ── 1. Require JSON ──────────────────────────────────────
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Content-Type must be application/json."
        }), 415

    # ── 2. Parse body ─────────────────────────────────────────
    try:
        data = request.get_json(force=False, silent=True)
    except Exception:
        data = None

    if data is None:
        return jsonify({
            "success": False,
            "error": "Invalid JSON body."
        }), 400

    # ── 3. Validate input ─────────────────────────────────────
    valid, error_msg = validate_chat_input(data)
    if not valid:
        return jsonify({
            "success": False,
            "error": error_msg
        }), 400

    user_message = data["message"].strip()
    session_id = data.get("session_id", "").strip() or None

    # ── 4. Get answer from chatbot ────────────────────────────
    try:
        db_path = os.environ.get("DATABASE_PATH") or None
        result = get_answer(
            user_message=user_message,
            session_id=session_id,
            db_path=db_path
        )
    except Exception as exc:
        # Log to stderr without exposing internal details to the client
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An internal error occurred. Please try again later."
        }), 500

    return jsonify(result), 200


@chat_bp.route("/api/chat/history", methods=["GET"])
def chat_history():
    """
    GET /api/chat/history?session_id=<id>&limit=<n>
    Returns the recent message history for a given session.
    """
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return jsonify({
            "success": False,
            "error": "Query parameter 'session_id' is required."
        }), 400

    try:
        limit = int(request.args.get("limit", 20))
        limit = max(1, min(limit, 100))  # clamp between 1 and 100
    except ValueError:
        limit = 20

    from services.database_service import get_chat_history
    import os
    db_path = os.environ.get("DATABASE_PATH") or None
    messages = get_chat_history(session_id, limit, db_path)

    return jsonify({
        "success": True,
        "session_id": session_id,
        "count": len(messages),
        "messages": messages
    }), 200
