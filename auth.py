"""
auth.py - Authentication system for AI Medicine Manager
Handles user signup, login, and session management using
hashed passwords stored in a local JSON file.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Optional

USERS_FILE = "data/users.json"


def _ensure_data_dir() -> None:
    """Create the data directory and users file if they don't exist."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)


def _load_users() -> dict:
    _ensure_data_dir()
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_users(users: dict) -> None:
    """
    Write the users file atomically: write to a temp file first, then
    rename it into place. This prevents a corrupted/half-written
    users.json (and everyone getting locked out) if the app is closed
    or killed at the exact moment it's saving.
    """
    _ensure_data_dir()
    tmp_path = USERS_FILE + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(users, f, indent=2)
    os.replace(tmp_path, USERS_FILE)


def _hash_password(password: str) -> str:
    """Return SHA-256 hash of a password with a fixed salt prefix."""
    salt = "ai_med_mgr_salt_2024"
    salted = f"{salt}{password}{salt}"
    return hashlib.sha256(salted.encode()).hexdigest()


def signup(username: str, password: str, email: str = "") -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users = _load_users()
    if username in users:
        return False, "Username already exists. Please choose another."

    users[username] = {
        "password_hash": _hash_password(password),
        "email": email.strip(),
        "created_at": datetime.now().isoformat(),
    }
    _save_users(users)
    return True, f"Account created successfully! Welcome, {username}."


def login(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate a user.
    Returns (success: bool, message: str).
    """
    username = username.strip().lower()
    if not username or not password:
        return False, "Please enter both username and password."

    users = _load_users()
    if username not in users:
        return False, "Invalid username or password."

    stored_hash = users[username]["password_hash"]
    if _hash_password(password) != stored_hash:
        return False, "Invalid username or password."

    return True, f"Welcome back, {username}!"


def user_exists(username: str) -> bool:
    users = _load_users()
    return username.strip().lower() in users


def get_user_info(username: str) -> Optional[dict]:
    users = _load_users()
    return users.get(username.strip().lower())
