"""
test/conftest.py — PyTest Fixtures
AI Chatbot for University Help Desk | KIET Group of Institutions

Provides shared fixtures:
    app      — Flask test application (in-memory SQLite, isolated)
    client   — Flask test client
    db_path  — path to in-memory test database

Usage:
    pytest test/              # run all tests
    pytest test/test_chat.py  # run specific module
"""

import os
import sys
import tempfile
import pytest

# Allow imports from src/backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))


@pytest.fixture(scope="function")
def db_path(tmp_path):
    """
    Provide a fresh temporary SQLite database for each test function.
    Uses a real file (not :memory:) so both the app and test code share it.
    """
    db_file = str(tmp_path / "test_chatbot.db")
    os.environ["DATABASE_PATH"] = db_file

    # Initialise schema
    from models import init_db
    init_db(db_file)

    yield db_file

    # Cleanup
    if "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]


@pytest.fixture(scope="function")
def app(db_path):
    """
    Create a Flask test application with an isolated in-memory database.
    """
    os.environ["FLASK_ENV"] = "testing"
    os.environ["ADMIN_API_KEY"] = "test-admin-key-12345"
    os.environ["DATABASE_PATH"] = db_path

    from app import create_app
    application = create_app(test_config={
        "TESTING": True,
        "DEBUG": True,
        "SECRET_KEY": "test-secret",
        "ADMIN_API_KEY": "test-admin-key-12345",
        "DATABASE_PATH": db_path,
    })

    yield application

    # Reset chatbot index after each test
    try:
        from services.chatbot_service import refresh_index
        refresh_index(db_path)
    except Exception:
        pass


@pytest.fixture(scope="function")
def client(app):
    """Return a Flask test client."""
    with app.test_client() as c:
        yield c


@pytest.fixture(scope="function")
def admin_headers():
    """Return HTTP headers with admin key."""
    return {
        "X-Admin-Key": "test-admin-key-12345",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="function")
def seeded_db(db_path):
    """
    Provide a database pre-populated with a small set of test FAQs.
    """
    from models.faq import create_faq
    create_faq(
        question="What is KIET?",
        answer="KIET Group of Institutions is a technical institution in Ghaziabad.",
        category="About KIET",
        source_url="https://www.kiet.edu/about-kiet",
        is_verified=1,
        db_path=db_path,
    )
    create_faq(
        question="Where is KIET located?",
        answer="KIET is located at 13 Km Milestone, Delhi-Meerut Expressway, Ghaziabad.",
        category="About KIET",
        source_url="https://www.kiet.edu/contact-us",
        is_verified=1,
        db_path=db_path,
    )
    create_faq(
        question="How do I get admission to KIET?",
        answer="B.Tech admission at KIET is through JEE Main and AKTU counselling.",
        category="Admissions",
        source_url="https://www.kiet.edu/admissions",
        is_verified=1,
        db_path=db_path,
    )
    create_faq(
        question="What is the contact number for KIET?",
        answer="Contact KIET at +91-120-2988300 or info@kiet.edu.",
        category="Contact",
        source_url="https://www.kiet.edu/contact-us",
        is_verified=1,
        db_path=db_path,
    )
    return db_path
