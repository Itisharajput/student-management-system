"""
auth.py
--------
Simple login system for the Student Management System.

Passwords are never stored in plain text. We hash them with SHA-256
plus a per-app salt before saving to the database. This is a
"good enough for a college project" approach — for a real production
system you would use something stronger like bcrypt or argon2.
"""

import hashlib
from database import Database

# A fixed salt is not ideal for production, but keeps this project
# dependency-free and easy to explain in an interview.
_SALT = "smsapp_static_salt_v1"


def hash_password(password: str) -> str:
    """Returns a SHA-256 hash of the password combined with a salt."""
    salted = (_SALT + password).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


class AuthManager:
    """Handles user registration and login checks against the DB."""

    def __init__(self, db: Database):
        self.db = db
        self._ensure_default_admin()

    def _ensure_default_admin(self):
        """
        Creates a default admin account (username: admin, password: admin123)
        the very first time the program runs, so the user always has a way
        to log in. They should change this password after first login.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", hash_password("admin123"), "admin"),
                )

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """Creates a new user account. Returns (success, message)."""
        username = username.strip()
        if not username or not password:
            return False, "Username and password cannot be empty."
        if len(password) < 4:
            return False, "Password must be at least 4 characters long."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, hash_password(password), "admin"),
                )
            return True, f"User '{username}' registered successfully."
        except Exception as exc:
            if "UNIQUE" in str(exc):
                return False, f"Username '{username}' is already taken."
            return False, f"Could not register user: {exc}"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Checks credentials. Returns (success, message)."""
        username = username.strip()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE username = ?", (username,)
                )
                row = cursor.fetchone()
        except Exception as exc:
            return False, f"Login failed due to a database error: {exc}"

        if row is None:
            return False, "No such username exists."
        if row["password_hash"] != hash_password(password):
            return False, "Incorrect password."
        return True, f"Welcome, {username}!"

    def change_password(self, username: str, new_password: str) -> tuple[bool, str]:
        """Updates the password for an existing user."""
        if len(new_password) < 4:
            return False, "Password must be at least 4 characters long."
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hash_password(new_password), username.strip()),
            )
            if cursor.rowcount == 0:
                return False, "No such username exists."
        return True, "Password updated successfully."
