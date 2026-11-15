"""
test/test_admin.py — Admin API Tests
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

import json
import os


class TestAdminAuthentication:
    """Tests for admin API authentication."""

    def test_admin_without_key_returns_401(self, client):
        """Missing X-Admin-Key should return 401."""
        response = client.get("/api/admin/faqs")
        assert response.status_code == 401

    def test_admin_with_wrong_key_returns_403(self, client):
        """Wrong admin key should return 403."""
        response = client.get(
            "/api/admin/faqs",
            headers={"X-Admin-Key": "wrong-key"}
        )
        assert response.status_code == 403

    def test_admin_with_correct_key_returns_200(self, client, admin_headers):
        """Correct admin key should allow access."""
        response = client.get("/api/admin/faqs", headers=admin_headers)
        assert response.status_code == 200

    def test_admin_unconfigured_server_key_returns_503(self, app, client):
        """When ADMIN_API_KEY is unset or placeholder, admin endpoint returns 503."""
        orig_conf = app.config.get("ADMIN_API_KEY")
        orig_env = os.environ.get("ADMIN_API_KEY")
        try:
            app.config["ADMIN_API_KEY"] = ""
            os.environ["ADMIN_API_KEY"] = ""
            response = client.get(
                "/api/admin/faqs",
                headers={"X-Admin-Key": "any-key"}
            )
            assert response.status_code == 503
            data = response.get_json()
            assert data["success"] is False
            assert "not configured" in data["error"].lower()
        finally:
            if orig_conf is not None:
                app.config["ADMIN_API_KEY"] = orig_conf
            if orig_env is not None:
                os.environ["ADMIN_API_KEY"] = orig_env


class TestAdminFAQCRUD:
    """Tests for FAQ create/read/update/delete via admin API."""

    def test_list_faqs_empty(self, client, admin_headers):
        """Empty DB should return empty list."""
        response = client.get("/api/admin/faqs", headers=admin_headers)
        data = response.get_json()
        assert data["success"] is True
        assert data["faqs"] == []
        assert data["count"] == 0

    def test_create_faq_success(self, client, admin_headers, db_path):
        """Should create a new FAQ and return 201."""
        payload = {
            "question": "What is KIET?",
            "answer": "KIET is a technical institution in Ghaziabad.",
            "category": "About KIET",
            "source_url": "https://www.kiet.edu/about-kiet",
            "is_verified": 1,
        }
        response = client.post(
            "/api/admin/faqs",
            data=json.dumps(payload),
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["faq"]["question"] == payload["question"]
        assert data["faq"]["id"] > 0

    def test_create_faq_missing_field(self, client, admin_headers):
        """Missing required fields should return 400."""
        payload = {"question": "Incomplete FAQ?"}
        response = client.post(
            "/api/admin/faqs",
            data=json.dumps(payload),
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_get_single_faq(self, client, admin_headers, db_path):
        """Should retrieve a single FAQ by id."""
        # Create one first
        payload = {
            "question": "Test Q?",
            "answer": "Test A.",
            "category": "Test",
        }
        create_resp = client.post(
            "/api/admin/faqs",
            data=json.dumps(payload),
            headers=admin_headers,
        )
        faq_id = create_resp.get_json()["faq"]["id"]

        # Retrieve it
        get_resp = client.get(f"/api/admin/faqs/{faq_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        data = get_resp.get_json()
        assert data["faq"]["id"] == faq_id

    def test_get_nonexistent_faq(self, client, admin_headers):
        """Non-existent FAQ id should return 404."""
        response = client.get("/api/admin/faqs/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_faq(self, client, admin_headers, db_path):
        """Should update a FAQ field and return the updated record."""
        # Create
        payload = {"question": "Old Q?", "answer": "Old A.", "category": "Cat"}
        created = client.post(
            "/api/admin/faqs", data=json.dumps(payload), headers=admin_headers
        ).get_json()["faq"]

        # Update
        update_resp = client.put(
            f"/api/admin/faqs/{created['id']}",
            data=json.dumps({"answer": "New A."}),
            headers=admin_headers,
        )
        assert update_resp.status_code == 200
        updated = update_resp.get_json()["faq"]
        assert updated["answer"] == "New A."
        assert updated["question"] == "Old Q?"  # unchanged

    def test_update_nonexistent_faq(self, client, admin_headers):
        """Updating a non-existent FAQ should return 404."""
        response = client.put(
            "/api/admin/faqs/99999",
            data=json.dumps({"answer": "X"}),
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_delete_faq(self, client, admin_headers, db_path):
        """Should delete a FAQ and return 200."""
        # Create
        payload = {"question": "Del Q?", "answer": "Del A.", "category": "Cat"}
        created = client.post(
            "/api/admin/faqs", data=json.dumps(payload), headers=admin_headers
        ).get_json()["faq"]

        # Delete
        del_resp = client.delete(
            f"/api/admin/faqs/{created['id']}", headers=admin_headers
        )
        assert del_resp.status_code == 200

        # Confirm gone
        get_resp = client.get(
            f"/api/admin/faqs/{created['id']}", headers=admin_headers
        )
        assert get_resp.status_code == 404

    def test_delete_nonexistent_faq(self, client, admin_headers):
        """Deleting a non-existent FAQ should return 404."""
        response = client.delete("/api/admin/faqs/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_search_faqs(self, client, admin_headers, db_path):
        """?search= param should filter results."""
        # Insert two FAQs
        for payload in [
            {"question": "Admission process?", "answer": "Via AKTU.", "category": "Admissions"},
            {"question": "Library hours?", "answer": "8am–8pm.", "category": "Facilities"},
        ]:
            client.post("/api/admin/faqs", data=json.dumps(payload), headers=admin_headers)

        response = client.get("/api/admin/faqs?search=admission", headers=admin_headers)
        data = response.get_json()
        assert data["success"] is True
        assert data["count"] >= 1
        assert all("admission" in r["question"].lower() for r in data["faqs"])

    def test_admin_stats(self, client, admin_headers, db_path):
        """GET /api/admin/stats should return db statistics."""
        response = client.get("/api/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "stats" in data
        assert "total_faqs" in data["stats"]
        assert "total_conversations" in data["stats"]
        assert "total_messages" in data["stats"]
