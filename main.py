import os
from nicegui import ui
from app.pages import register
from dotenv import load_dotenv
load_dotenv()  

register()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Finance Pathway",
        port=int(os.environ.get("PORT", 8080)),
        storage_secret=os.environ.get("STORAGE_SECRET", "dev-only-change-me"),
        reload=False,
        show=False,
    )