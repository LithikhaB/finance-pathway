from nicegui import ui

from app.services import auth

STATE = {"mode": "login"}


def login_page() -> None:
    from app.theme import AMBER, frame

    if auth.current_user():
        ui.navigate.to("/")
        return

    STATE["mode"] = "login"

    with frame(show_calculator=False):
        ui.label("Finance Pathway").classes("text-3xl serif")
        ui.label(
            "No real accounts here, just a name to keep your progress separate. "
            "Everything resets when the app restarts."
        ).classes("muted")

        with ui.column().classes("w-full max-w-sm gap-3 mt-4"):
            title = ui.label("Log in").classes("text-2xl serif")
            username = ui.input("Username").classes("w-full").props("autofocus").mark("login-username")
            password = ui.input("Password", password=True).classes("w-full").mark("login-password")
            error = ui.label().style(f"color:{AMBER}")

            def submit() -> None:
                u, p = (username.value or "").strip(), password.value or ""
                if not u or not p:
                    error.text = "Enter a username and a password."
                    return
                if STATE["mode"] == "login":
                    if auth.verify(u, p):
                        auth.login(u)
                        ui.navigate.to("/")
                    else:
                        error.text = "Incorrect username or password."
                else:
                    ok, msg = auth.register(u, p)
                    if ok:
                        auth.login(u)
                        ui.navigate.to("/")
                    else:
                        error.text = msg

            submit_btn = ui.button("Log in", on_click=submit).classes("w-full")
            password.on("keydown.enter", submit)

            def toggle() -> None:
                STATE["mode"] = "signup" if STATE["mode"] == "login" else "login"
                signing_up = STATE["mode"] == "signup"
                title.text = "Create an account" if signing_up else "Log in"
                submit_btn.text = "Sign up" if signing_up else "Log in"
                switch.text = "Already have an account? Log in" if signing_up else "New here? Create an account"
                error.text = ""

            switch = ui.button("New here? Create an account", on_click=toggle).props("flat dense")