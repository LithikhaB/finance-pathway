"""SQLite persistence for accounts and quiz progress.

A single file database, created on first run, is what lets progress and
logins survive an app restart. The path can be overridden with the
FINANCE_PATHWAY_DB environment variable (used by the test suite so tests
never touch the real database).
"""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "app.db"


def _db_path() -> Path:
    override = os.environ.get("FINANCE_PATHWAY_DB")
    path = Path(override) if override else _DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init() -> None:
    """Create tables if they don't already exist. Safe to call on every startup."""
    with connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS progress (
                username TEXT NOT NULL,
                module_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                done INTEGER NOT NULL,
                PRIMARY KEY (username, module_id)
            )"""
        )