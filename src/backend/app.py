"""
app.py — Flask Application Factory
AI Chatbot for University Help Desk | KIET Group of Institutions

Team:
  Anant Singh   — Frontend Development
  Agraj Dixit   — Backend, AI Integration & Coordination
  Amlesh Singh  — Deployment, Documentation & Testing

Run (from src/backend/):
    python app.py

Or via Flask CLI (from src/backend/):
    flask run
"""

import os
import sys

from flask import Flask, jsonify
from config import get_config
from models import init_db
from routes import all_blueprints


def create_app(test_config: dict = None) -> Flask:
    """
    Application factory.

    Args:
        test_config: Optional dict of config overrides (used in tests).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # ── Load configuration ──────────────────────────────────
    cfg = get_config()
    app.config.from_object(cfg)

    if test_config:
        app.config.update(test_config)

    # Propagate DB path from app config to environment
    if app.config.get("DATABASE_PATH"):
        os.environ["DATABASE_PATH"] = app.config["DATABASE_PATH"]

    if app.config.get("ADMIN_API_KEY"):
        os.environ["ADMIN_API_KEY"] = app.config["ADMIN_API_KEY"]

    # Ensure production environment enforces DEBUG=False and validates configuration
    env_name = os.getenv("FLASK_ENV", "development").lower()
    if env_name == "production" or (not app.config.get("TESTING") and cfg.__name__ == "ProductionConfig"):
        from config import ProductionConfig
        ProductionConfig.validate(app.config)
        app.config["DEBUG"] = False

    # ── Serve Frontend UI ───────────────────────────────────
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/chat")
    def serve_chat_ui():
        from flask import send_from_directory
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/style.css")
    def serve_style_css():
        from flask import send_from_directory
        return send_from_directory(frontend_dir, "style.css")

    @app.route("/script.js")
    def serve_script_js():
        from flask import send_from_directory
        return send_from_directory(frontend_dir, "script.js")

    @app.route("/frontend/<path:filename>")
    def serve_frontend_file(filename):
        from flask import send_from_directory
        return send_from_directory(frontend_dir, filename)

    # ── Register route blueprints ───────────────────────────
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # ── Root endpoint ───────────────────────────────────────
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "app": app.config["APP_NAME"],
            "version": app.config["APP_VERSION"],
            "institution": app.config["INSTITUTION"],
            "status": "running",
            "endpoints": {
                "health":    "GET  /api/health",
                "chat":      "POST /api/chat",
                "history":   "GET  /api/chat/history?session_id=<id>",
                "admin_faqs":"GET  /api/admin/faqs  (requires X-Admin-Key header)",
            }
        }), 200

    # ── Global error handlers ───────────────────────────────
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"success": False, "error": "Endpoint not found.", "code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"success": False, "error": "Method not allowed.", "code": 405}), 405

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"success": False, "error": "Internal server error.", "code": 500}), 500

    # ── Initialise the database ─────────────────────────────
    db_path = os.environ.get("DATABASE_PATH") or None
    if db_path != ":memory:":
        init_db(db_path)

    # ── Warm up the TF-IDF index (non-blocking — zero FAQs is fine) ─
    try:
        from services.chatbot_service import initialise_chatbot
        count = initialise_chatbot(db_path if db_path != ":memory:" else None)
        if not app.config.get("TESTING"):
            print(f"  TF-IDF index loaded — {count} FAQ(s) indexed.")
    except Exception as exc:
        if not app.config.get("TESTING"):
            print(f"  Warning: TF-IDF index not loaded: {exc}")

    return app


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    application = create_app()
    cfg = get_config()

    print("=" * 55)
    print("  KIET AI Chatbot — Flask Server Starting")
    print("  Phase 2: Backend Development")
    print(f"  Running on http://{cfg.HOST}:{cfg.PORT}")
    print("=" * 55)

    application.run(
        host=cfg.HOST,
        port=cfg.PORT,
        debug=cfg.DEBUG
    )
