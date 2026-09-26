"""A small floating chat widget. Unlike the calculator (which only appears
during a quiz), this is available on every page: click the bubble in the
bottom-right corner to open a chat panel, ask a finance question, and get
an answer from `app.services.chatbot`.
"""
from nicegui import ui

from app.services import chatbot
from app.theme import INK, MUTED, PAPER, RULE, TEAL

_BUBBLE_STYLE = (
    "position:fixed; bottom:24px; right:24px; z-index:1000; "
    f"background:{TEAL}; color:#FFFFFF; border-radius:50%; width:56px; height:56px; "
    "box-shadow:0 4px 14px rgba(0,0,0,0.25);"
)
# Fixed total height (not flex-based) so every section inside gets real,
# predictable space instead of collapsing to zero.
_PANEL_HIDDEN = (
    "position:fixed; bottom:92px; right:24px; z-index:1000; width:320px; max-width:calc(100vw - 32px); "
    "height:420px; "
    f"background:#FFFFFF; border:1px solid {RULE}; border-radius:10px; "
    "box-shadow:0 8px 30px rgba(0,0,0,0.18); display:none; flex-direction:column; overflow:hidden;"
)
_PANEL_VISIBLE = _PANEL_HIDDEN.replace("display:none", "display:flex")


def chat_widget() -> None:
    panel = ui.column().classes("chat-panel gap-0").style(_PANEL_HIDDEN)
    with panel:
        with ui.row().classes("w-full items-center justify-between px-3 py-2").style(
            f"background:{INK}; flex-shrink:0;"
        ):
            ui.label("Ask about finance").classes("text-white text-sm font-medium")
            close_btn = ui.button(icon="close").props("flat round dense size=sm color=white")

        # Fixed pixel height + overflow-y auto, deliberately not a flex-sized
        # ui.scroll_area, which collapses to 0 height without an explicit
        # pixel height on every ancestor.
        messages = ui.column().classes("w-full gap-2 p-3").style(
            "height:288px; overflow-y:auto; flex-shrink:0;"
        )
        with messages:
            ui.label(
                "Ask me about any term from the curriculum: compound interest, "
                "EMI, NPV, KYC, and so on."
            ).classes("text-sm").style(f"color:{MUTED};")

        with ui.row().classes("w-full gap-1 p-2 items-end").style(
            f"border-top:1px solid {RULE}; flex-shrink:0;"
        ):
            question = ui.textarea(placeholder="Ask a question...").classes("grow").props(
                "dense outlined autogrow rows=1"
            ).mark("chat-question-input")
            send_btn = ui.button(icon="send").props("flat round dense").mark("chat-send-button")

    bubble = ui.button(icon="chat").style(_BUBBLE_STYLE).mark("chat-bubble")

    def add_message(role: str, text: str) -> None:
        with messages:
            align = "items-end" if role == "user" else "items-start"
            bg = TEAL if role == "user" else PAPER
            fg = "#FFFFFF" if role == "user" else INK
            with ui.column().classes(f"w-full {align} gap-0"):
                ui.label(text).style(
                    f"background:{bg}; color:{fg}; border-radius:10px; padding:8px 12px; "
                    "max-width:85%; white-space:pre-wrap;"
                )
        ui.run_javascript(
            "setTimeout(() => { const els = document.querySelectorAll('.chat-panel > div'); "
            "if (els[1]) els[1].scrollTop = els[1].scrollHeight; }, 50);"
        )

    def open_panel() -> None:
        panel.style(replace=_PANEL_VISIBLE)
        bubble.style(replace=_BUBBLE_STYLE + " display:none;")

    def close_panel() -> None:
        panel.style(replace=_PANEL_HIDDEN)
        bubble.style(replace=_BUBBLE_STYLE)

    def send() -> None:
        text = (question.value or "").strip()
        if not text:
            return
        add_message("user", text)
        question.value = ""
        try:
            answer = chatbot.ask(text)
        except Exception as exc:  # last-resort safety net so failures are visible, not silent
            answer = f"Something went wrong answering that ({exc.__class__.__name__}). Please try again."
        add_message("bot", answer)

    bubble.on_click(open_panel)
    close_btn.on_click(close_panel)
    send_btn.on_click(send)
    question.on("keydown.enter", send)