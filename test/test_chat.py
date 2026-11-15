"""
test/test_chat.py — Chat API Tests
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

import json
import os


class TestChatEndpointValidation:
    """Tests for input validation on POST /api/chat."""

    def test_chat_requires_json_content_type(self, client):
        """Non-JSON Content-Type should return 415."""
        response = client.post("/api/chat", data="hello", content_type="text/plain")
        assert response.status_code == 415

    def test_chat_rejects_empty_message(self, client):
        """Empty message string should return 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data

    def test_chat_rejects_whitespace_only_message(self, client):
        """Whitespace-only message should return 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "   "}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_rejects_missing_message_field(self, client):
        """Missing 'message' key should return 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"query": "hello"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_rejects_non_string_message(self, client):
        """Non-string message should return 400."""
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": 12345}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_rejects_too_long_message(self, client):
        """Message exceeding max length should return 400."""
        long_message = "a" * 501
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": long_message}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_chat_rejects_invalid_json(self, client):
        """Malformed JSON body should return 400."""
        response = client.post(
            "/api/chat",
            data="this is not json",
            content_type="application/json",
        )
        assert response.status_code == 400


class TestChatEndpointResponses:
    """Tests for chat response correctness."""

    def test_chat_returns_200_for_valid_message(self, client, seeded_db, db_path):
        """Valid message should return 200."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "What is KIET?"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_chat_response_has_required_fields(self, client, seeded_db, db_path):
        """Response must contain success, answer, category, source, confidence."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "Tell me about KIET"}),
            content_type="application/json",
        )
        data = response.get_json()
        assert "success" in data
        assert "answer" in data
        assert "category" in data
        assert "confidence" in data
        assert "session_id" in data

    def test_chat_confidence_is_float(self, client, seeded_db, db_path):
        """Confidence score must be a float between 0.0 and 1.0."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "Where is KIET located?"}),
            content_type="application/json",
        )
        data = response.get_json()
        confidence = data.get("confidence")
        assert isinstance(confidence, (int, float))
        assert 0.0 <= confidence <= 1.0

    def test_chat_confidence_is_calculated_not_fabricated(self, client, seeded_db, db_path):
        """
        A very different query should return low confidence.
        Verifies the score reflects actual similarity.
        """
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "xyzxyz random gibberish query"}),
            content_type="application/json",
        )
        data = response.get_json()
        # Gibberish should have very low or zero confidence
        assert data["confidence"] < 0.5

    def test_chat_unknown_query_returns_fallback(self, client, seeded_db, db_path):
        """
        A query with no match should return a fallback message,
        not invented KIET information.
        """
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "zyxwvutsrqponmlkjihgfedcba"}),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["success"] is True
        # Fallback should contain guidance to official site
        assert "kiet.edu" in data["answer"].lower() or "help desk" in data["answer"].lower()

    def test_chat_session_id_returned(self, client, seeded_db, db_path):
        """Response must include a session_id."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "KIET location"}),
            content_type="application/json",
        )
        data = response.get_json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_chat_session_id_preserved(self, client, seeded_db, db_path):
        """If a session_id is provided, it must be echoed back."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)

        my_session = "test-session-abc-123"
        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "KIET admission", "session_id": my_session}),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["session_id"] == my_session

    def test_chat_empty_knowledge_base_returns_graceful_message(self, client, db_path):
        """With an empty FAQ table, the bot should respond gracefully."""
        os.environ["DATABASE_PATH"] = db_path
        from services.chatbot_service import refresh_index
        refresh_index(db_path)   # empty DB

        response = client.post(
            "/api/chat",
            data=json.dumps({"message": "What is KIET?"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
