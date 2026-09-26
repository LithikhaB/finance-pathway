"""Accounts, now backed by SQLite so they survive an app restart.

Passwords are hashed (PBKDF2-SHA256 with a random salt per user), which is
a real improvement over the earlier plain-text, in-memory version, though
this is still a small demo auth system, not a production-grade one (no
rate limiting, no password reset, no email verification).
"""
import hashlib
import os
import sqlite3

from nicegui import app

from app.services.db import connect, init

init()

_ITERATIONS = 200_000


def _hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS).hex()


def register(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Enter a username and a password."
    salt = os.urandom(16)
    password_hash = _hash(password, salt)
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt.hex()),
            )
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    return True, ""


def verify(username: str, password: str) -> bool:
    username = username.strip()
    with connect() as conn:
        row = conn.execute(
            "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        return False
    return _hash(password, bytes.fromhex(row["salt"])) == row["password_hash"]


def login(username: str) -> None:
    app.storage.user["username"] = username.strip()


def logout() -> None:
    app.storage.user.pop("username", None)


def current_user() -> str | None:
    try:
        return app.storage.user.get("username")
    except RuntimeError:
        # No active NiceGUI client context (e.g. called from a plain test).
        return None