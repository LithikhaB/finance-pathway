"""In-memory progress. No login yet, so there is one shared state that
resets every time the app is restarted (`python main.py`).

When login and per-user profiles are added, swap `_STATE` for a lookup keyed
by user id (e.g. backed by SQLite) without touching the pages: only the
functions below are used by the UI.
"""

PASS_RATIO = 0.6

_STATE: dict[str, dict] = {}


def record_score(module_id: int, score: int, total: int) -> dict:
    previous = _STATE.get(str(module_id), {}).get("score", 0)
    best = max(previous, score)
    entry = {"score": best, "total": total, "done": best / total >= PASS_RATIO}
    _STATE[str(module_id)] = entry
    return entry


def get(module_id: int) -> dict | None:
    return _STATE.get(str(module_id))


def completed_count() -> int:
    return sum(1 for e in _STATE.values() if e.get("done"))


def reset() -> None:
    """Clear all progress. Exposed for tests and for a future 'start over' button."""
    _STATE.clear()