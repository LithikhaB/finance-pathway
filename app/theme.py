from contextlib import contextmanager

from nicegui import ui

from app.services import auth

PAPER = "#F3F5F7"
INK = "#12213A"
TEAL = "#0F766E"
AMBER = "#B45309"
MUTED = "#5B6778"
RULE = "#D5DBE3"

_CSS = f"""
body {{ background: {PAPER}; color: {INK}; font-family: 'IBM Plex Sans', system-ui, sans-serif; }}
h1, h2, h3, .serif {{ font-family: 'IBM Plex Serif', Georgia, serif; }}
.muted {{ color: {MUTED}; }}
.module-row {{ border-top: 1px solid {RULE}; padding: 14px 0; }}
.module-row:last-child {{ border-bottom: 1px solid {RULE}; }}
.note {{ border-left: 3px solid {TEAL}; padding: 4px 0 4px 14px; }}
.stat-value {{ font-family: 'IBM Plex Serif', Georgia, serif; font-size: 1.6rem; }}
a.plain {{ color: inherit; text-decoration: none; }}
a.plain:hover {{ text-decoration: underline; }}
:focus-visible {{ outline: 2px solid {TEAL}; outline-offset: 2px; }}

/* Formulas, laid out like a textbook rather than a code snippet. */
.formula {{
    font-family: 'IBM Plex Serif', Georgia, serif;
    font-size: 1.2rem;
    background: #FFFFFF;
    border: 1px solid {RULE};
    border-radius: 4px;
    padding: 14px 18px;
    margin: 10px 0;
    overflow-x: auto;
    white-space: nowrap;
}}
.formula .var {{ font-style: italic; }}
.formula .frac {{
    display: inline-flex;
    flex-direction: column;
    vertical-align: middle;
    text-align: center;
    margin: 0 6px;
    line-height: 1.3;
}}
.formula .frac .num {{ padding: 0 6px 3px; border-bottom: 1.5px solid {INK}; }}
.formula .frac .den {{ padding: 3px 6px 0; }}
.formula .key {{ color: {MUTED}; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.9rem; white-space: normal; }}

/* Calculator sits to the right and follows scroll; hidden until a quiz is on screen. */
.layout-row {{ flex-wrap: nowrap; }}
.calc-sidebar {{ width: 240px; flex-shrink: 0; position: sticky; top: 88px; display: none; }}
.calc-sidebar.calc-visible {{ display: block; }}
@media (max-width: 900px) {{
    .layout-row {{ flex-wrap: wrap; }}
    .calc-sidebar {{ position: static; width: 100%; max-width: 320px; }}
}}
.calc-close {{ position: absolute; top: 6px; right: 6px; }}
"""

_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600'
    '&family=IBM+Plex+Serif:wght@500;600&display=swap" rel="stylesheet">'
)


@contextmanager
def frame(show_home_link: bool = True, show_calculator: bool = True, show_chat: bool = True):
    """Shared page chrome: header, main content column, an optional calculator
    that only appears once a quiz scrolls into view, and an optional floating
    chat bubble available throughout the app."""
    from app.components.calculator import calculator  # lazy: avoids circular import
    from app.components.chat import chat_widget  # lazy: avoids circular import

    ui.add_head_html(_FONTS)
    ui.add_css(_CSS)
    ui.colors(primary=TEAL)
    with ui.header(elevated=False).classes("items-center px-4 py-3").style(
        f"background:{INK}"
    ):
        ui.link("Finance Pathway", "/").classes("plain serif text-lg text-white")
        ui.space()
        user = auth.current_user()
        if user:
            ui.label(user).classes("text-white text-sm mr-2")
            ui.button(
                icon="logout",
                on_click=lambda: (auth.logout(), ui.navigate.to("/login")),
            ).props("flat round dense color=white").tooltip("Log out").mark("logout-button")
        ui.label("Educational use only. Not financial advice.").classes(
            "text-xs text-white opacity-70"
        )

    with ui.row().classes(
        "w-full max-w-6xl mx-auto px-4 py-8 gap-8 items-start justify-center layout-row"
    ):
        with ui.column().classes("w-full max-w-3xl gap-6 min-w-0"):
            yield
        if show_calculator:
            with ui.column().classes("calc-sidebar gap-2"):
                calculator()
            # Reveal the calculator only while a quiz section is on screen.
            ui.run_javascript(
                """
                (function() {
                    const panel = document.querySelector('.calc-sidebar');
                    if (!panel || panel.dataset.observed) return;
                    panel.dataset.observed = '1';
                    let closedManually = false;
                    window.__closeCalcPanel = function() {
                        panel.classList.remove('calc-visible');
                        closedManually = true;
                    };
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach((entry) => {
                            if (entry.isIntersecting) {
                                if (!closedManually) panel.classList.add('calc-visible');
                            } else {
                                panel.classList.remove('calc-visible');
                                closedManually = false;
                            }
                        });
                    }, { threshold: 0.15 });
                    document.querySelectorAll('.quiz-anchor').forEach((el) => observer.observe(el));
                })();
                """
            )
        if show_chat:
            chat_widget()