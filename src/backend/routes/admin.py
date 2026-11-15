"""
routes/admin.py — Admin API Endpoints (FAQ CRUD + Stats)
AI Chatbot for University Help Desk | KIET Group of Institutions

All admin endpoints require the HTTP header:
    X-Admin-Key: <value of ADMIN_API_KEY in .env>

Endpoints:
    GET    /api/admin/stats          — database statistics
    GET    /api/admin/faqs           — list all FAQs (optional ?category= ?search=)
    GET    /api/admin/faqs/<id>      — single FAQ
    POST   /api/admin/faqs           — create a new FAQ
    PUT    /api/admin/faqs/<id>      — update a FAQ
    DELETE /api/admin/faqs/<id>      — delete a FAQ
    POST   /api/admin/index/rebuild  — rebuild the NLP index
"""

import os
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from services.database_service import (
    list_faqs, find_faq, find_faqs_by_keyword,
    add_faq, edit_faq, remove_faq, get_stats
)
from services.chatbot_service import refresh_index
from utils.validators import validate_faq_input

admin_bp = Blueprint("admin", __name__)

INSECURE_ADMIN_KEYS = {
    "",
    "your-strong-admin-key-here",
    "your-admin-key-here",
    "replace-with-a-secure-confidential-admin-key",
    "change-me",
    "admin",
}


# ──────────────────────────────────────────────
# Authentication decorator
# ──────────────────────────────────────────────

def require_admin_key(f):
    """
    Decorator that checks the X-Admin-Key header against the ADMIN_API_KEY
    environment variable or app config. Returns 401/403/503 on failure.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        expected_key = (
            current_app.config.get("ADMIN_API_KEY")
            or os.environ.get("ADMIN_API_KEY", "")
        )
        expected_key = str(expected_key).strip()

        # If ADMIN_API_KEY is not set or matches known insecure placeholders, refuse access
        if not expected_key or expected_key.lower() in INSECURE_ADMIN_KEYS:
            return jsonify({
                "success": False,
                "error": "Admin access is not configured. Set ADMIN_API_KEY in environment."
            }), 503

        provided_key = request.headers.get("X-Admin-Key", "").strip()
        if not provided_key:
            return jsonify({
                "success": False,
                "error": "Missing 'X-Admin-Key' header."
            }), 401

        # Constant-time comparison to prevent timing attacks
        import hmac
        if not hmac.compare_digest(expected_key, provided_key):
            return jsonify({
                "success": False,
                "error": "Invalid admin key."
            }), 403

        return f(*args, **kwargs)
    return wrapper


def _db_path():
    return os.environ.get("DATABASE_PATH") or None


# ──────────────────────────────────────────────
# Stats
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/stats", methods=["GET"])
@require_admin_key
def admin_stats():
    """Return aggregate statistics."""
    stats = get_stats(_db_path())
    return jsonify({"success": True, "stats": stats}), 200


# ──────────────────────────────────────────────
# FAQ List & Search
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/faqs", methods=["GET"])
@require_admin_key
def admin_list_faqs():
    """
    GET /api/admin/faqs
    Optional query params:
        ?category=Admissions
        ?search=hostel
    """
    category = request.args.get("category", "").strip() or None
    search = request.args.get("search", "").strip() or None

    if search:
        faqs = find_faqs_by_keyword(search, _db_path())
    else:
        faqs = list_faqs(category, _db_path())

    return jsonify({
        "success": True,
        "count": len(faqs),
        "faqs": faqs
    }), 200


# ──────────────────────────────────────────────
# Single FAQ
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/faqs/<int:faq_id>", methods=["GET"])
@require_admin_key
def admin_get_faq(faq_id: int):
    """GET /api/admin/faqs/<id>"""
    faq = find_faq(faq_id, _db_path())
    if not faq:
        return jsonify({"success": False, "error": f"FAQ #{faq_id} not found."}), 404
    return jsonify({"success": True, "faq": faq}), 200


# ──────────────────────────────────────────────
# Create FAQ
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/faqs", methods=["POST"])
@require_admin_key
def admin_create_faq():
    """
    POST /api/admin/faqs
    Body: { "question": "...", "answer": "...", "category": "...",
            "source_url": "...", "is_verified": 0|1 }
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json."}), 415

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body."}), 400

    valid, err = validate_faq_input(data)
    if not valid:
        return jsonify({"success": False, "error": err}), 400

    faq = add_faq(
        question=data["question"].strip(),
        answer=data["answer"].strip(),
        category=data["category"].strip(),
        source_url=data.get("source_url", "").strip() or None,
        is_verified=int(data.get("is_verified", 0)),
        last_verified=data.get("last_verified"),
        db_path=_db_path()
    )

    # Rebuild NLP index to include the new FAQ
    refresh_index(_db_path())

    return jsonify({"success": True, "faq": faq}), 201


# ──────────────────────────────────────────────
# Update FAQ
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/faqs/<int:faq_id>", methods=["PUT"])
@require_admin_key
def admin_update_faq(faq_id: int):
    """PUT /api/admin/faqs/<id>"""
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json."}), 415

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body."}), 400

    existing = find_faq(faq_id, _db_path())
    if not existing:
        return jsonify({"success": False, "error": f"FAQ #{faq_id} not found."}), 404

    valid, err = validate_faq_input(data, is_update=True)
    if not valid:
        return jsonify({"success": False, "error": err}), 400

    updated = edit_faq(faq_id, data, _db_path())
    if not updated:
        return jsonify({"success": False, "error": f"FAQ #{faq_id} not found."}), 404

    refresh_index(_db_path())
    return jsonify({"success": True, "faq": updated}), 200


# ──────────────────────────────────────────────
# Delete FAQ
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/faqs/<int:faq_id>", methods=["DELETE"])
@require_admin_key
def admin_delete_faq(faq_id: int):
    """DELETE /api/admin/faqs/<id>"""
    deleted = remove_faq(faq_id, _db_path())
    if not deleted:
        return jsonify({"success": False, "error": f"FAQ #{faq_id} not found."}), 404

    refresh_index(_db_path())
    return jsonify({"success": True, "message": f"FAQ #{faq_id} deleted."}), 200


# ──────────────────────────────────────────────
# Rebuild NLP Index
# ──────────────────────────────────────────────

@admin_bp.route("/api/admin/index/rebuild", methods=["POST"])
@require_admin_key
def admin_rebuild_index():
    """POST /api/admin/index/rebuild — Force a TF-IDF index rebuild."""
    refresh_index(_db_path())
    from services.nlp_service import get_engine
    size = get_engine().corpus_size
    return jsonify({
        "success": True,
        "message": f"TF-IDF index rebuilt successfully.",
        "faqs_indexed": size
    }), 200
