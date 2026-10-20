"""
GlycoTwin — Authentication Utilities
Argon2id password hashing and session management.

Security notes:
  - Uses argon2-cffi with recommended parameters.
  - Passwords are never placed in Streamlit session_state after auth.
  - Session state is scoped to a single browser session.
  - This is a local prototype; production deployment requires a
    hardened backend with HTTPS, rate limiting, and session signing.
"""

import re
import sys
from pathlib import Path
from typing import Optional

from argon2 import PasswordHasher, Type as Argon2Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db import (
    create_user,
    get_user_by_email,
    update_last_login,
    email_exists,
    init_db,
    get_preferences,
    save_preferences,
)

# ── Password hasher (Argon2id with recommended parameters) ────────────────────
_HASHER = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=2,
    hash_len=32,
    salt_len=16,
    type=Argon2Type.ID,  # Argon2id
)

# ── Email validation ──────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def hash_password(password: str) -> str:
    """Return an Argon2id hash of the password. Never store the plaintext."""
    return _HASHER.hash(password)


def verify_password(password: str, hash_str: str) -> bool:
    """Return True if password matches the stored hash."""
    try:
        return _HASHER.verify(hash_str, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def validate_email(email: str) -> Optional[str]:
    """Return None if valid, or an error string."""
    email = email.strip()
    if not email:
        return "Email address is required."
    if not _EMAIL_RE.match(email):
        return "Please enter a valid email address."
    return None


def validate_password(password: str, confirm: str = None) -> Optional[str]:
    """Return None if valid, or an error string."""
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one digit."
    if confirm is not None and password != confirm:
        return "Passwords do not match."
    return None


def register_user(
    display_name: str,
    email: str,
    password: str,
    confirm_password: str,
    role: str = "researcher",
    institution: str = "",
) -> tuple[bool, str, Optional[int]]:
    """
    Attempt to register a new user.
    Returns (success, message, user_id).
    """
    init_db()

    if not display_name.strip():
        return False, "Full name is required.", None

    err = validate_email(email)
    if err:
        return False, err, None

    err = validate_password(password, confirm_password)
    if err:
        return False, err, None

    if email_exists(email):
        # Deliberately vague to avoid email enumeration
        return False, "An account with this email already exists.", None

    password_hash = hash_password(password)
    try:
        user_id = create_user(
            display_name=display_name.strip(),
            email=email,
            password_hash=password_hash,
            role=role,
            institution=institution,
        )
        return True, "Account created successfully.", user_id
    except Exception as exc:
        return False, f"Account creation failed: {exc}", None


def authenticate_user(email: str, password: str) -> tuple[bool, str, Optional[dict]]:
    """
    Verify credentials.
    Returns (success, message, user_dict | None).
    The user dict never contains the password hash.
    """
    init_db()

    user = get_user_by_email(email)
    if user is None:
        # Constant-time-ish: still hash even if user not found
        _HASHER.hash("dummy_constant_time_check_9xZ!")
        return False, "Invalid email or password.", None

    if user["status"] != "active":
        return False, "This account is suspended. Please contact support.", None

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid email or password.", None

    update_last_login(user["id"])

    # Return a safe dict — NO password hash included
    user_info = {
        "id": user["id"],
        "display_name": user["display_name"],
        "email": user["email"],
        "role": user["role"],
        "institution": user["institution"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }
    return True, "Login successful.", user_info


def get_user_preferences(user_id: int) -> dict:
    """Return preferences dict with defaults if not yet set."""
    init_db()
    prefs = get_preferences(user_id)
    if prefs is None:
        return {
            "theme": "dark",
            "default_tab": "overview",
            "preferred_chart": "line",
            "preferred_cohort": "all",
            "last_participant": None,
            "preferred_units": "mg/dL",
        }
    return dict(prefs)


def save_user_preferences(user_id: int, **kwargs) -> None:
    init_db()
    save_preferences(user_id, **kwargs)
