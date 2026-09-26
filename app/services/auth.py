"""A deliberately small login system for a portfolio demo.

Not for production: passwords are kept in plain text in memory, and every
account disappears when the server restarts, same as quiz progress. It
exists to give each learner a name so progress can be kept separate
within a single run, and to give the app a login screen to show off.
"""
from nicegui import app

_USERS: dict[str, str] = {}


def register(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Enter a username and a password."
    if username in _USERS:
        return False, "That username is already taken."
    _USERS[username] = password
    return True, ""


def verify(username: str, password: str) -> bool:
    return _USERS.get(username.strip()) == password


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