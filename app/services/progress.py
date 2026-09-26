"""Quiz progress, backed by SQLite so it survives an app restart and is
kept separate per signed-in username. The functions below are the only
thing pages call, so the storage underneath can change without touching
any page.
"""
from app.services import auth
from app.services.db import connect, init

init()

PASS_RATIO = 0.6


def _username() -> str:
    return auth.current_user() or "guest"


def record_score(module_id: int, score: int, total: int) -> dict:
    username = _username()
    with connect() as conn:
        row = conn.execute(
            "SELECT score FROM progress WHERE username = ? AND module_id = ?",
            (username, module_id),
        ).fetchone()
        previous = row["score"] if row else 0
        best = max(previous, score)
        done = 1 if best / total >= PASS_RATIO else 0
        conn.execute(
            """INSERT INTO progress (username, module_id, score, total, done)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(username, module_id) DO UPDATE SET
                   score = excluded.score, total = excluded.total, done = excluded.done""",
            (username, module_id, best, total, done),
        )
    return {"score": best, "total": total, "done": bool(done)}


def get(module_id: int) -> dict | None:
    username = _username()
    with connect() as conn:
        row = conn.execute(
            "SELECT score, total, done FROM progress WHERE username = ? AND module_id = ?",
            (username, module_id),
        ).fetchone()
    if row is None:
        return None
    return {"score": row["score"], "total": row["total"], "done": bool(row["done"])}


def completed_count() -> int:
    username = _username()
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM progress WHERE username = ? AND done = 1",
            (username,),
        ).fetchone()
    return row["c"]


def reset() -> None:
    """Clear the current user's progress. Exposed for tests and a future 'start over' button."""
    username = _username()
    with connect() as conn:
        conn.execute("DELETE FROM progress WHERE username = ?", (username,))