"""In-memory progress, kept separate per signed-in username.

Everything lives in a plain dict, so it resets whenever the app is
restarted (`python main.py`) — there is no database yet. Swap `_STATE`
for a real lookup (e.g. SQLite keyed by username) later without touching
the pages: only the functions below are used by the UI.
"""
from app.services import auth

PASS_RATIO = 0.6

_STATE: dict[str, dict[str, dict]] = {}


def _user_state() -> dict[str, dict]:
    username = auth.current_user() or "guest"
    return _STATE.setdefault(username, {})


def record_score(module_id: int, score: int, total: int) -> dict:
    state = _user_state()
    previous = state.get(str(module_id), {}).get("score", 0)
    best = max(previous, score)
    entry = {"score": best, "total": total, "done": best / total >= PASS_RATIO}
    state[str(module_id)] = entry
    return entry


def get(module_id: int) -> dict | None:
    return _user_state().get(str(module_id))


def completed_count() -> int:
    return sum(1 for e in _user_state().values() if e.get("done"))


def reset() -> None:
    """Clear the current user's progress. Exposed for tests and a future 'start over' button."""
    _user_state().clear()