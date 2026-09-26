from nicegui import ui

from app.services import progress
from app.theme import AMBER, TEAL


def quiz(module_id: int, questions: list[dict]) -> None:
    """Interview-style multiple choice quiz. Records the best score."""
    radios = []
    with ui.column().classes("w-full gap-5 quiz-anchor"):
        for i, q in enumerate(questions, start=1):
            with ui.column().classes("gap-1 w-full"):
                ui.label(f"{i}. {q['q']}").classes("font-medium")
                radios.append(ui.radio(q["options"]).props("dense"))

        result = ui.column().classes("w-full gap-2")

        def check() -> None:
            if any(r.value is None for r in radios):
                ui.notify("Answer every question first.", type="warning")
                return
            result.clear()
            score = 0
            with result:
                for i, (q, r) in enumerate(zip(questions, radios), start=1):
                    correct = r.value == q["options"][q["answer"]]
                    score += correct
                    colour = TEAL if correct else AMBER
                    verdict = "Correct." if correct else "Not quite."
                    ui.markdown(f"**{i}. {verdict}** {q['why']}").style(f"color:{colour}")
                entry = progress.record_score(module_id, score, len(questions))
                ui.label(
                    f"Score: {score}/{len(questions)}. Best: {entry['score']}/{entry['total']}."
                ).classes("font-medium")
                if entry["done"]:
                    ui.label("Module complete.").style(f"color:{TEAL}")
                else:
                    ui.label("Re-read the lesson and try again to complete this module.").classes("muted")

        ui.button("Check answers", on_click=check)