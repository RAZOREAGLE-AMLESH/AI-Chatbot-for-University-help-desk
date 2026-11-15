"""
test/test_database.py — Database Operation Tests
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

import os


class TestFAQModel:
    """Tests for FAQ CRUD operations."""

    def test_create_faq(self, db_path):
        """Should create a FAQ and return it with an id."""
        from models.faq import create_faq
        faq = create_faq(
            question="Test question?",
            answer="Test answer.",
            category="Test",
            db_path=db_path,
        )
        assert faq is not None
        assert faq["id"] > 0
        assert faq["question"] == "Test question?"
        assert faq["answer"] == "Test answer."
        assert faq["category"] == "Test"

    def test_get_faq_by_id(self, db_path):
        """Should retrieve a FAQ by its id."""
        from models.faq import create_faq, get_faq_by_id
        created = create_faq("Q?", "A.", "Cat", db_path=db_path)
        retrieved = get_faq_by_id(created["id"], db_path)
        assert retrieved is not None
        assert retrieved["id"] == created["id"]

    def test_get_faq_by_id_not_found(self, db_path):
        """Non-existent id should return None."""
        from models.faq import get_faq_by_id
        result = get_faq_by_id(99999, db_path)
        assert result is None

    def test_get_all_faqs_empty(self, db_path):
        """Empty table should return empty list."""
        from models.faq import get_all_faqs
        faqs = get_all_faqs(db_path)
        assert faqs == []

    def test_get_all_faqs_with_records(self, db_path):
        """Should return all inserted FAQs."""
        from models.faq import create_faq, get_all_faqs
        create_faq("Q1?", "A1.", "Cat1", db_path=db_path)
        create_faq("Q2?", "A2.", "Cat2", db_path=db_path)
        faqs = get_all_faqs(db_path)
        assert len(faqs) == 2

    def test_update_faq(self, db_path):
        """Should update specified fields only."""
        from models.faq import create_faq, update_faq
        faq = create_faq("Old question?", "Old answer.", "Old Cat", db_path=db_path)
        updated = update_faq(faq["id"], {"answer": "New answer."}, db_path)
        assert updated["answer"] == "New answer."
        assert updated["question"] == "Old question?"  # unchanged

    def test_update_faq_not_found(self, db_path):
        """Updating a non-existent FAQ should return None."""
        from models.faq import update_faq
        result = update_faq(99999, {"answer": "New."}, db_path)
        assert result is None

    def test_delete_faq(self, db_path):
        """Should delete the FAQ and return True."""
        from models.faq import create_faq, delete_faq, get_faq_by_id
        faq = create_faq("Q?", "A.", "Cat", db_path=db_path)
        deleted = delete_faq(faq["id"], db_path)
        assert deleted is True
        assert get_faq_by_id(faq["id"], db_path) is None

    def test_delete_faq_not_found(self, db_path):
        """Deleting a non-existent FAQ should return False."""
        from models.faq import delete_faq
        result = delete_faq(99999, db_path)
        assert result is False

    def test_search_faqs(self, db_path):
        """Should find FAQs matching a keyword."""
        from models.faq import create_faq, search_faqs
        create_faq("How to apply for admission?", "Apply via AKTU counselling.", "Admissions", db_path=db_path)
        create_faq("Library timings?", "Library is open 8am-8pm.", "Facilities", db_path=db_path)
        results = search_faqs("admission", db_path)
        assert len(results) >= 1
        assert any("admission" in r["question"].lower() for r in results)

    def test_count_faqs(self, db_path):
        """count_faqs should return the correct number."""
        from models.faq import create_faq, count_faqs
        assert count_faqs(db_path) == 0
        create_faq("Q?", "A.", "Cat", db_path=db_path)
        assert count_faqs(db_path) == 1
        create_faq("Q2?", "A2.", "Cat", db_path=db_path)
        assert count_faqs(db_path) == 2

    def test_faq_has_created_at(self, db_path):
        """Created FAQ should have a non-null created_at timestamp."""
        from models.faq import create_faq
        faq = create_faq("Q?", "A.", "Cat", db_path=db_path)
        assert faq["created_at"] is not None
        assert len(faq["created_at"]) > 0

    def test_is_verified_default_zero(self, db_path):
        """is_verified should default to 0."""
        from models.faq import create_faq
        faq = create_faq("Q?", "A.", "Cat", db_path=db_path)
        assert faq["is_verified"] == 0


class TestConversationModel:
    """Tests for Conversation and Message models."""

    def test_create_conversation(self, db_path):
        """get_or_create_conversation should create a new conversation."""
        from models.conversation import get_or_create_conversation
        conv = get_or_create_conversation("session-001", db_path)
        assert conv is not None
        assert conv["session_id"] == "session-001"
        assert conv["id"] > 0

    def test_get_existing_conversation(self, db_path):
        """get_or_create_conversation should return existing record."""
        from models.conversation import get_or_create_conversation
        conv1 = get_or_create_conversation("session-002", db_path)
        conv2 = get_or_create_conversation("session-002", db_path)
        assert conv1["id"] == conv2["id"]

    def test_save_and_retrieve_messages(self, db_path):
        """Messages should be retrievable by session_id."""
        from models.conversation import (
            get_or_create_conversation, save_message, get_messages_for_session
        )
        conv = get_or_create_conversation("session-003", db_path)
        save_message(conv["id"], "user", "Hello KIET!", db_path=db_path)
        save_message(conv["id"], "bot", "Welcome to KIET.", confidence=0.9, db_path=db_path)
        messages = get_messages_for_session("session-003", db_path=db_path)
        assert len(messages) == 2
        assert messages[0]["sender"] == "user"
        assert messages[1]["sender"] == "bot"

    def test_message_confidence_stored(self, db_path):
        """Bot message confidence should be persisted."""
        from models.conversation import (
            get_or_create_conversation, save_message, get_messages_for_session
        )
        conv = get_or_create_conversation("session-004", db_path)
        save_message(conv["id"], "bot", "Answer.", confidence=0.75, db_path=db_path)
        messages = get_messages_for_session("session-004", db_path=db_path)
        assert abs(messages[0]["confidence"] - 0.75) < 0.001

    def test_count_conversations(self, db_path):
        """count_conversations should reflect actual count."""
        from models.conversation import get_or_create_conversation, count_conversations
        assert count_conversations(db_path) == 0
        get_or_create_conversation("s1", db_path)
        get_or_create_conversation("s2", db_path)
        assert count_conversations(db_path) == 2
