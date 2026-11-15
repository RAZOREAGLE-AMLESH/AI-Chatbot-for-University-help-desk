"""
test/test_health.py — Health Endpoint Tests
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

import json


class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        """GET /api/health should return HTTP 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """GET /api/health should return valid JSON."""
        response = client.get("/api/health")
        data = response.get_json()
        assert data is not None

    def test_health_status_ok(self, client):
        """GET /api/health should include status: ok."""
        response = client.get("/api/health")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_contains_institution(self, client):
        """GET /api/health should mention KIET."""
        response = client.get("/api/health")
        data = response.get_json()
        assert "KIET" in data.get("institution", "") or "KIET" in data.get("app", "")

    def test_root_returns_200(self, client):
        """GET / should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_endpoints(self, client):
        """GET / should list available API endpoints."""
        response = client.get("/")
        data = response.get_json()
        assert "endpoints" in data

    def test_404_for_unknown_route(self, client):
        """Unknown route should return 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_404_response_is_json(self, client):
        """404 response should be JSON."""
        response = client.get("/api/nonexistent")
        data = response.get_json()
        assert data is not None
        assert data["success"] is False

    def test_endpoints_do_not_expose_wildcard_cors(self, client):
        """API endpoints should not inject wildcard Access-Control-Allow-Origin."""
        response = client.get("/api/health")
        assert response.headers.get("Access-Control-Allow-Origin") != "*"


class TestConfigurationAndDeployment:
    """Tests for environment configuration and production safety."""

    def test_production_rejects_default_or_missing_secret_key(self, monkeypatch):
        """ProductionConfig.validate must raise ValueError if SECRET_KEY is missing or default."""
        import pytest
        from config import ProductionConfig

        monkeypatch.setenv("SECRET_KEY", "change-me-in-production")
        with pytest.raises(ValueError, match="SECRET_KEY is missing, default, or weak"):
            ProductionConfig.validate()

        monkeypatch.setenv("SECRET_KEY", "")
        with pytest.raises(ValueError, match="SECRET_KEY is missing, default, or weak"):
            ProductionConfig.validate()

    def test_production_rejects_short_secret_key(self, monkeypatch):
        """ProductionConfig.validate must raise ValueError if SECRET_KEY is under 16 chars."""
        import pytest
        from config import ProductionConfig

        monkeypatch.setenv("SECRET_KEY", "short-secret")
        with pytest.raises(ValueError, match="SECRET_KEY is missing, default, or weak"):
            ProductionConfig.validate()

    def test_production_rejects_invalid_port(self, monkeypatch):
        """ProductionConfig.validate must raise ValueError if PORT is invalid."""
        import pytest
        from config import ProductionConfig

        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("PORT", "not-a-port")
        with pytest.raises(ValueError, match="PORT must be an integer between 1 and 65535"):
            ProductionConfig.validate()

        monkeypatch.setenv("PORT", "99999")
        with pytest.raises(ValueError, match="PORT must be an integer between 1 and 65535"):
            ProductionConfig.validate()

    def test_production_accepts_strong_secret_key(self, monkeypatch):
        """ProductionConfig.validate succeeds with strong SECRET_KEY and valid PORT."""
        from config import ProductionConfig

        monkeypatch.setenv("SECRET_KEY", "prod-secret-token-32-chars-long!")
        monkeypatch.setenv("PORT", "8000")
        ProductionConfig.validate()
        assert ProductionConfig.DEBUG is False

    def test_safe_port_parsing(self, monkeypatch):
        """_get_safe_port should handle valid, invalid, and missing ports gracefully."""
        from config import _get_safe_port

        monkeypatch.setenv("PORT", "8080")
        assert _get_safe_port(5000) == 8080

        monkeypatch.setenv("PORT", "invalid")
        assert _get_safe_port(5000) == 5000

        monkeypatch.setenv("PORT", "-10")
        assert _get_safe_port(5000) == 5000

        monkeypatch.delenv("PORT", raising=False)
        assert _get_safe_port(5000) == 5000
