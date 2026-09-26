"""A small four-function calculator, meant to sit beside a lesson so the
learner can check a number without leaving the page. Runs entirely on the
server side (no eval, no JavaScript arithmetic) using a simple accumulator
model, the same one a physical calculator uses. It is shown or hidden by
the page frame based on scroll position; the close button here just lets
the learner dismiss it early.
"""
from nicegui import ui

from app.theme import INK, MUTED, PAPER, RULE, TEAL

_OPS = {
    "+": lambda a, b: a + b,
    "\u2212": lambda a, b: a - b,
    "\u00d7": lambda a, b: a * b,
    "\u00f7": lambda a, b: a / b if b != 0 else float("nan"),
}

_OP_INACTIVE = f"background:#FFFFFF; color:{TEAL}; border:1px solid {TEAL}; min-width:0;"
_OP_ACTIVE = f"background:{TEAL}; color:#FFFFFF; border:1px solid {TEAL}; min-width:0;"
_EQUALS = f"background:{INK}; color:#FFFFFF; border:1px solid {INK}; min-width:0;"
_DIGIT = f"background:#FFFFFF; color:{INK}; border:1px solid {RULE}; min-width:0;"
_UTILITY = f"background:{PAPER}; color:{MUTED}; border:1px solid {RULE}; min-width:0;"


def _format(value: float) -> str:
    if value != value:  # NaN
        return "Error"
    if value == int(value) and abs(value) < 1e15:
        return f"{int(value):,}"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


def calculator() -> None:
    state = {"acc": 0.0, "op": None, "entry": "0", "fresh": True}
    op_buttons: dict[str, ui.button] = {}

    with ui.column().classes("gap-2 w-full p-3").style(
        f"background:#FFFFFF; border:1px solid {RULE}; border-radius:8px; position:relative;"
    ):
        ui.button(icon="close", on_click=lambda: ui.run_javascript(
            "window.__closeCalcPanel && window.__closeCalcPanel()"
        )).props("flat round dense size=sm").classes("calc-close")

        ui.label("Calculator").classes("text-sm muted")
        display = ui.label("0").classes("w-full text-right").style(
            f"font-family:'IBM Plex Serif',Georgia,serif; font-size:1.4rem; color:{INK};"
            "padding:6px 4px; overflow-wrap:anywhere;"
        )

        def refresh_display() -> None:
            display.text = state["entry"]

        def refresh_active_op() -> None:
            for op, button in op_buttons.items():
                button.style(replace=_OP_ACTIVE if state["op"] == op else _OP_INACTIVE)

        def digit(d: str) -> None:
            if state["fresh"] or state["entry"] == "0":
                state["entry"] = d
                state["fresh"] = False
            else:
                state["entry"] += d
            refresh_display()

        def dot() -> None:
            if state["fresh"]:
                state["entry"], state["fresh"] = "0.", False
            elif "." not in state["entry"]:
                state["entry"] += "."
            refresh_display()

        def choose_op(op: str) -> None:
            _resolve()
            state["acc"] = float(state["entry"])
            state["op"] = op
            state["fresh"] = True
            refresh_active_op()

        def _resolve() -> None:
            if state["op"] is not None:
                result = _OPS[state["op"]](state["acc"], float(state["entry"]))
                state["entry"] = _format(result)

        def equals() -> None:
            _resolve()
            state["op"] = None
            state["fresh"] = True
            refresh_display()
            refresh_active_op()

        def clear() -> None:
            state.update(acc=0.0, op=None, entry="0", fresh=True)
            refresh_display()
            refresh_active_op()

        def backspace() -> None:
            if not state["fresh"] and len(state["entry"]) > 1:
                state["entry"] = state["entry"][:-1]
            else:
                state["entry"], state["fresh"] = "0", True
            refresh_display()

        def pct() -> None:
            state["entry"] = _format(float(state["entry"]) / 100)
            refresh_display()

        def digit_btn(label: str, on_click):
            return ui.button(label, on_click=on_click).classes("grow").style(_DIGIT)

        def utility_btn(label: str, on_click):
            return ui.button(label, on_click=on_click).classes("grow").style(_UTILITY)

        def op_btn(label: str, op: str):
            button = ui.button(label, on_click=lambda: choose_op(op)).classes("grow").style(_OP_INACTIVE)
            op_buttons[op] = button
            return button

        with ui.row().classes("gap-1 w-full no-wrap"):
            utility_btn("C", clear)
            utility_btn("\u232b", backspace)
            utility_btn("%", pct)
            op_btn("\u00f7", "\u00f7")
        with ui.row().classes("gap-1 w-full no-wrap"):
            digit_btn("7", lambda: digit("7"))
            digit_btn("8", lambda: digit("8"))
            digit_btn("9", lambda: digit("9"))
            op_btn("\u00d7", "\u00d7")
        with ui.row().classes("gap-1 w-full no-wrap"):
            digit_btn("4", lambda: digit("4"))
            digit_btn("5", lambda: digit("5"))
            digit_btn("6", lambda: digit("6"))
            op_btn("\u2212", "\u2212")
        with ui.row().classes("gap-1 w-full no-wrap"):
            digit_btn("1", lambda: digit("1"))
            digit_btn("2", lambda: digit("2"))
            digit_btn("3", lambda: digit("3"))
            op_btn("+", "+")
        with ui.row().classes("gap-1 w-full no-wrap"):
            digit_btn("0", lambda: digit("0"))
            digit_btn(".", dot)
            ui.button("=", on_click=equals).classes("grow").style(_EQUALS)