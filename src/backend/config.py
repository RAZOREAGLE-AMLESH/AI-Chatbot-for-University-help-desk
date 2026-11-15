"""
config.py — Application Configuration
AI Chatbot for University Help Desk | KIET Group of Institutions

Reads environment variables from a .env file (manual fallback parser included
so the app works even if python-dotenv is not installed).
"""

import os
import pathlib


# ──────────────────────────────────────────────
# Minimal .env loader (fallback when python-dotenv is absent)
# ──────────────────────────────────────────────

def _load_env_file() -> None:
    """
    Parse a .env file in the project root and populate os.environ.
    Existing environment variables are NOT overwritten (setdefault semantics).
    Lines beginning with '#' and blank lines are ignored.
    """
    # Walk up from src/backend to the project root
    backend_dir = pathlib.Path(__file__).parent
    project_root = backend_dir.parent.parent
    env_path = project_root / ".env"

    if not env_path.exists():
        return

    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")   # remove optional quotes
            os.environ.setdefault(key, value)


_load_env_file()

# Try python-dotenv if installed (richer .env support)
try:
    from dotenv import load_dotenv
    _root = pathlib.Path(__file__).parent.parent.parent / ".env"
    load_dotenv(_root, override=False)
except ImportError:
    pass   # manual loader above is sufficient


# ──────────────────────────────────────────────
# Safe port parsing and weak secret detection
# ──────────────────────────────────────────────

def _get_safe_port(default: int = 5000) -> int:
    """
    Safely parse and validate the PORT environment variable.
    Returns integer port if valid (1-65535); falls back to default on invalid inputs.
    """
    port_val = os.getenv("PORT")
    if not port_val:
        return default
    try:
        port = int(port_val)
        if 1 <= port <= 65535:
            return port
        return default
    except (ValueError, TypeError):
        return default


INSECURE_SECRET_KEYS = {
    "",
    "change-me-in-production",
    "your-secret-key-change-this-in-production",
    "replace-with-a-secure-random-secret-key-min-16-chars",
    "secret",
    "secretkey",
    "secret-key",
    "password",
    "dev-secret-key",
    "test-secret",
    "12345678",
    "admin",
}


# ──────────────────────────────────────────────
# Config classes
# ──────────────────────────────────────────────

class Config:
    """Shared base configuration."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")

    DEBUG: bool = False
    TESTING: bool = False

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = _get_safe_port(5000)

    # Application metadata
    APP_NAME: str = "KIET AI Chatbot"
    APP_VERSION: str = "2.0.0"
    INSTITUTION: str = "KIET Group of Institutions, Ghaziabad"

    # Database — defaults to <project_root>/instance/chatbot.db
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "")


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = os.getenv("HOST", "0.0.0.0")


class ProductionConfig(Config):
    DEBUG = False
    HOST = os.getenv("HOST", "0.0.0.0")

    @classmethod
    def validate(cls, config_dict: dict = None) -> None:
        """
        Validate production configuration safety rules:
        1. DEBUG must be False.
        2. SECRET_KEY must be provided, cannot match known weak defaults,
           and must be at least 16 characters long.
        3. PORT (if explicitly set) must be an integer between 1 and 65535.
        """
        cls.DEBUG = False

        # Validate SECRET_KEY
        secret_key = None
        if config_dict and "SECRET_KEY" in config_dict:
            secret_key = config_dict["SECRET_KEY"]
        if not secret_key:
            secret_key = os.getenv("SECRET_KEY", "")

        secret_key = str(secret_key).strip()
        if not secret_key or secret_key.lower() in INSECURE_SECRET_KEYS or len(secret_key) < 16:
            raise ValueError(
                "Production configuration error: SECRET_KEY is missing, default, or weak. "
                "Set a strong SECRET_KEY (minimum 16 characters) in the environment before starting in production."
            )

        # Validate PORT
        port_raw = os.getenv("PORT")
        if port_raw:
            try:
                port_num = int(port_raw)
                if not (1 <= port_num <= 65535):
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError(
                    f"Production configuration error: PORT must be an integer between 1 and 65535, got {port_raw!r}."
                )


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # In-memory SQLite for tests — set via env in conftest
    DATABASE_PATH = os.getenv("DATABASE_PATH", ":memory:")


_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Return the appropriate config class based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development").lower()
    config_class = _CONFIG_MAP.get(env, DevelopmentConfig)
    if env == "production" or config_class is ProductionConfig:
        ProductionConfig.validate()
    return config_class
