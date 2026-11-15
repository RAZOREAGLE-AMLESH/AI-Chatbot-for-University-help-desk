"""
routes/__init__.py — Blueprint Registry
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

from .health import health_bp
from .chat import chat_bp
from .admin import admin_bp

all_blueprints = [
    health_bp,
    chat_bp,
    admin_bp,
]
