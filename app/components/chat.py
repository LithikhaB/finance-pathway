"""A small floating chat widget. Unlike the calculator (which only appears
during a quiz), this is available on every page: click the bubble in the
bottom-right corner to open a chat panel, ask a finance question, and get
an answer from `app.services.chatbot`. Drag the "Ask about finance" title
bar to move the panel anywhere on screen (see the drag script in theme.py).
"""
from nicegui import ui

from app.services import chatbot
from app.theme import INK, MUTED, PAPER, RULE, TEAL


def chat_widget() -> None:
    panel = ui.column().classes("chat-panel gap-0")
    with panel:
        with ui.row().classes("w-full items-center justify-between px-3 py-2 chat-header").style(
            f"background:{INK}; flex-shrink:0;"
        ):
            ui.label("Ask about finance").classes("text-white text-sm font-medium").style(
                "user-select:none;"
            )
            close_btn = ui.button(icon="close").props("flat round dense size=sm color=white").mark(
                "chat-close-button"
            )

        # Flexes to fill whatever space is left after the header and input
        # row take theirs, so the input row (and send button) is never
        # pushed out of view by a growing message list or a tall textarea.
        messages = ui.column().classes("w-full gap-2 p-3").style(
            "flex:1; min-height:0; overflow-y:auto;"
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

    bubble = ui.button(icon="chat").classes("chat-bubble").mark("chat-bubble")

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
            "setTimeout(() => { const m = document.querySelector('.chat-panel > div:nth-child(2)'); "
            "if (m) m.scrollTop = m.scrollHeight; }, 50);"
        )

    def open_panel() -> None:
        panel.classes(add="chat-open")
        bubble.classes(add="chat-bubble-hidden")

    def close_panel() -> None:
        panel.classes(remove="chat-open")
        bubble.classes(remove="chat-bubble-hidden")

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