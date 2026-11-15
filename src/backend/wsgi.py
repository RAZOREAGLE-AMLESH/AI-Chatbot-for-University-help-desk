"""
wsgi.py — Web Server Gateway Interface Entry Point
AI Chatbot for University Help Desk | KIET Group of Institutions

Usage (Linux with Gunicorn from project root):
    gunicorn --chdir src/backend wsgi:app --bind 0.0.0.0:5000 --workers 4
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
