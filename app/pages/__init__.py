from nicegui import ui

from app.pages import home, login
from app.pages.modules import (
    module1, module2, module3, module4, module5,
    module6, module7, module8, module9, module10,
)
from app.services import auth


def _protected(page_func):
    """Redirect to /login if no one is signed in, otherwise render the page."""
    def wrapper() -> None:
        if not auth.current_user():
            ui.navigate.to("/login")
            return
        page_func()
    return wrapper


def register() -> None:
    """Attach every page to its route. Add new modules here."""
    ui.page("/login")(login.login_page)
    ui.page("/")(_protected(home.home))
    ui.page("/module/1")(_protected(module1.module_1))
    ui.page("/module/2")(_protected(module2.module_2))
    ui.page("/module/3")(_protected(module3.module_3))
    ui.page("/module/4")(_protected(module4.module_4))
    ui.page("/module/5")(_protected(module5.module_5))
    ui.page("/module/6")(_protected(module6.module_6))
    ui.page("/module/7")(_protected(module7.module_7))
    ui.page("/module/8")(_protected(module8.module_8))
    ui.page("/module/9")(_protected(module9.module_9))
    ui.page("/module/10")(_protected(module10.module_10))