"""
utils/validators.py — Input Validation Utilities
AI Chatbot for University Help Desk | KIET Group of Institutions

All user-facing inputs are validated here before reaching the database or NLP layer.
"""

import re


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
MAX_MESSAGE_LENGTH = 500
MAX_FAQ_QUESTION_LENGTH = 300
MAX_FAQ_ANSWER_LENGTH = 2000
MIN_MESSAGE_LENGTH = 2


def validate_chat_input(data: dict) -> tuple[bool, str]:
    """
    Validate incoming chat request payload.

    Returns:
        (True, "") on success
        (False, error_message) on failure
    """
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object."

    message = data.get("message", "")

    if not isinstance(message, str):
        return False, "'message' must be a string."

    message = message.strip()

    if len(message) < MIN_MESSAGE_LENGTH:
        return False, "Message is too short. Please enter at least 2 characters."

    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message is too long. Maximum allowed length is {MAX_MESSAGE_LENGTH} characters."

    # Reject messages that are only special characters
    if not re.search(r'[a-zA-Z0-9]', message):
        return False, "Message must contain at least one letter or digit."

    return True, ""


def validate_faq_input(data: dict, is_update: bool = False) -> tuple[bool, str]:
    """
    Validate incoming FAQ create/update payload.

    Returns:
        (True, "") on success
        (False, error_message) on failure
    """
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object."

    required_fields = ["question", "answer", "category"] if not is_update else []

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: '{field}'."

    question = data.get("question", "")
    answer = data.get("answer", "")
    category = data.get("category", "")

    if question and len(question.strip()) < 5:
        return False, "Question is too short (minimum 5 characters)."

    if question and len(question.strip()) > MAX_FAQ_QUESTION_LENGTH:
        return False, f"Question exceeds maximum length of {MAX_FAQ_QUESTION_LENGTH} characters."

    if answer and len(answer.strip()) < 5:
        return False, "Answer is too short (minimum 5 characters)."

    if answer and len(answer.strip()) > MAX_FAQ_ANSWER_LENGTH:
        return False, f"Answer exceeds maximum length of {MAX_FAQ_ANSWER_LENGTH} characters."

    if category and not re.match(r'^[a-zA-Z0-9 _\-]+$', category.strip()):
        return False, "Category can only contain letters, numbers, spaces, hyphens, and underscores."

    return True, ""


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Strip and truncate a string value safely."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]
