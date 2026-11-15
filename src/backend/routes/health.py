"""
health.py — Health Check Route
AI Chatbot for University Help Desk | KIET Group of Institutions

Endpoint: GET /api/health
Returns server status and app metadata.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    Used to verify the Flask server is running correctly.
    """
    app_name = current_app.config.get("APP_NAME", "AI Chatbot for University Help Desk")
    version = current_app.config.get("APP_VERSION", "2.0.0")
    institution = current_app.config.get("INSTITUTION", "KIET Group of Institutions, Ghaziabad")

    return jsonify({
        "status": "ok",
        "message": "KIET AI Chatbot server is running.",
        "app": app_name,
        "institution": institution,
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200
