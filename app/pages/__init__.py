from nicegui import ui

from app.pages import home
from app.pages.modules import (
    module1, module2, module3, module4, module5,
    module6, module7, module8, module9, module10,
)


def register() -> None:
    """Attach every page to its route. Add new modules here."""
    ui.page("/")(home.home)
    ui.page("/module/1")(module1.module_1)
    ui.page("/module/2")(module2.module_2)
    ui.page("/module/3")(module3.module_3)
    ui.page("/module/4")(module4.module_4)
    ui.page("/module/5")(module5.module_5)
    ui.page("/module/6")(module6.module_6)
    ui.page("/module/7")(module7.module_7)
    ui.page("/module/8")(module8.module_8)
    ui.page("/module/9")(module9.module_9)
    ui.page("/module/10")(module10.module_10)