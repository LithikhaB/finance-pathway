from nicegui import ui

from app import content
from app.services import progress
from app.theme import TEAL


def home() -> None:
    from app.theme import frame

    with frame(show_calculator=False):
        ui.label("Learn the finance behind fintech, in the right order.").classes(
            "text-4xl leading-tight"
        ).props("role=heading aria-level=1").classes("serif")
        ui.label(
            "Ten modules covering how money moves, how it is priced, how risk is "
            "managed and what regulators require. Each has a short lesson, a "
            "calculator and an interview-style quiz."
        ).classes("muted text-lg")

        live = content.live_modules()
        done = progress.completed_count()
        with ui.column().classes("w-full gap-1"):
            ui.label(f"{done} of {len(live)} available modules complete").classes("text-sm muted")
            ui.linear_progress(value=done / len(live) if live else 0, show_value=False).props(
                f"color=teal-8 track-color=grey-4 size=8px"
            )

        for stage in content.STAGES:
            with ui.column().classes("w-full gap-0 mt-4"):
                ui.label(stage["name"]).classes("text-xl serif")
                ui.label(stage["tagline"]).classes("muted mb-2")
                for m in stage["modules"]:
                    entry = progress.get(m["id"])
                    with ui.row().classes("module-row w-full items-center no-wrap"):
                        with ui.column().classes("gap-0 grow"):
                            if m["live"]:
                                ui.link(f"{m['id']}. {m['title']}", f"/module/{m['id']}").classes(
                                    "plain font-medium text-lg"
                                )
                            else:
                                ui.label(f"{m['id']}. {m['title']}").classes("font-medium text-lg muted")
                            ui.label(m["summary"]).classes("muted text-sm")
                        if m["live"]:
                            if entry and entry.get("done"):
                                ui.label(f"Done, {entry['score']}/{entry['total']}").style(f"color:{TEAL}")
                            else:
                                ui.button("Start", on_click=lambda mid=m["id"]: ui.navigate.to(f"/module/{mid}")).props(
                                    "flat dense"
                                )
                        else:
                            ui.label("Coming soon").classes("muted text-sm")

        with ui.column().classes("w-full gap-0 mt-6"):
            ui.label("Tools").classes("text-xl serif")
            ui.label("Extra ways to explore, outside the module order.").classes("muted mb-2")
            with ui.row().classes("module-row w-full items-center no-wrap"):
                with ui.column().classes("gap-0 grow"):
                    ui.link("Company lookup", "/company").classes("plain font-medium text-lg")
                    ui.label(
                        "See what a company does, how it earns, and how it moves money."
                    ).classes("muted text-sm")
                ui.button("Open", on_click=lambda: ui.navigate.to("/company")).props("flat dense")