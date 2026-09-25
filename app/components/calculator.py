"""A small four-function calculator, meant to sit beside a lesson so the
learner can check a number without leaving the page. Runs entirely on the
server side (no eval, no JavaScript) using a simple accumulator model, the
same one a physical calculator uses.
"""
from nicegui import ui

from app.theme import INK, MUTED, RULE, TEAL

_OPS = {
    "+": lambda a, b: a + b,
    "\u2212": lambda a, b: a - b,
    "\u00d7": lambda a, b: a * b,
    "\u00f7": lambda a, b: a / b if b != 0 else float("nan"),
}


def _format(value: float) -> str:
    if value != value:  # NaN
        return "Error"
    if value == int(value) and abs(value) < 1e15:
        return f"{int(value):,}"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


def calculator() -> None:
    state = {"acc": 0.0, "op": None, "entry": "0", "fresh": True}

    with ui.column().classes("gap-2 w-full p-3").style(
        f"background:#FFFFFF; border:1px solid {RULE}; border-radius:8px;"
    ):
        ui.label("Calculator").classes("text-sm muted")
        display = ui.label("0").classes("w-full text-right").style(
            f"font-family:'IBM Plex Serif',Georgia,serif; font-size:1.4rem; color:{INK};"
            "padding:6px 4px; overflow-wrap:anywhere;"
        )

        def refresh() -> None:
            display.text = state["entry"]

        def digit(d: str) -> None:
            if state["fresh"] or state["entry"] == "0":
                state["entry"] = d
                state["fresh"] = False
            else:
                state["entry"] += d
            refresh()

        def dot() -> None:
            if state["fresh"]:
                state["entry"], state["fresh"] = "0.", False
            elif "." not in state["entry"]:
                state["entry"] += "."
            refresh()

        def choose_op(op: str) -> None:
            _resolve()
            state["acc"] = float(state["entry"])
            state["op"] = op
            state["fresh"] = True

        def _resolve() -> None:
            if state["op"] is not None:
                result = _OPS[state["op"]](state["acc"], float(state["entry"]))
                state["entry"] = _format(result)

        def equals() -> None:
            _resolve()
            state["op"] = None
            state["fresh"] = True
            refresh()

        def clear() -> None:
            state.update(acc=0.0, op=None, entry="0", fresh=True)
            refresh()

        def backspace() -> None:
            if not state["fresh"] and len(state["entry"]) > 1:
                state["entry"] = state["entry"][:-1]
            else:
                state["entry"], state["fresh"] = "0", True
            refresh()

        def pct() -> None:
            state["entry"] = _format(float(state["entry"]) / 100)
            refresh()

        def btn(label: str, on_click, accent: bool = False):
            colour = TEAL if accent else INK
            return ui.button(label, on_click=on_click).props("flat").classes(
                "grow"
            ).style(f"color:{colour}; border:1px solid {RULE}; min-width:0;")

        with ui.row().classes("gap-1 w-full no-wrap"):
            btn("C", clear)
            btn("\u232b", backspace)
            btn("%", pct)
            btn("\u00f7", lambda: choose_op("\u00f7"), accent=True)
        with ui.row().classes("gap-1 w-full no-wrap"):
            btn("7", lambda: digit("7"))
            btn("8", lambda: digit("8"))
            btn("9", lambda: digit("9"))
            btn("\u00d7", lambda: choose_op("\u00d7"), accent=True)
        with ui.row().classes("gap-1 w-full no-wrap"):
            btn("4", lambda: digit("4"))
            btn("5", lambda: digit("5"))
            btn("6", lambda: digit("6"))
            btn("\u2212", lambda: choose_op("\u2212"), accent=True)
        with ui.row().classes("gap-1 w-full no-wrap"):
            btn("1", lambda: digit("1"))
            btn("2", lambda: digit("2"))
            btn("3", lambda: digit("3"))
            btn("+", lambda: choose_op("+"), accent=True)
        with ui.row().classes("gap-1 w-full no-wrap"):
            btn("0", lambda: digit("0"))
            btn(".", dot)
            btn("=", equals, accent=True)