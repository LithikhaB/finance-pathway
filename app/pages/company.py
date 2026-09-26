from nicegui import ui

from app.services import chatbot

EXAMPLES = ["Citigroup", "Stripe", "Paytm", "Razorpay", "PayPal", "JPMorgan Chase", "Robinhood"]


def company_page() -> None:
    from app.theme import MUTED, frame

    with frame(show_calculator=False):
        ui.label("Company lookup").classes("text-3xl serif")
        ui.label(
            "Enter a company name to see what it does, how it makes money, "
            "and how it moves or manages funds."
        ).classes("muted text-lg")

        with ui.row().classes("w-full gap-2 items-end flex-wrap mt-2"):
            name_input = ui.input("Company name", placeholder="e.g. Citigroup").classes("w-72").mark(
                "company-name-input"
            )
            lookup_btn = ui.button("Look up").mark("company-lookup-button")

        with ui.row().classes("gap-2 flex-wrap mt-1"):
            ui.label("Try:").classes("text-sm").style(f"color:{MUTED};")
            for example in EXAMPLES:
                ui.button(
                    example, on_click=lambda e=example: (name_input.set_value(e), run_lookup())
                ).props("flat dense")

        spinner = ui.spinner(size="md").classes("mt-4")
        spinner.visible = False
        result = ui.column().classes("w-full gap-2 mt-2")

        def run_lookup() -> None:
            name = (name_input.value or "").strip()
            if not name:
                ui.notify("Enter a company name first.", type="warning")
                return
            result.clear()
            spinner.visible = True
            try:
                answer = chatbot.explain_company(name)
            finally:
                spinner.visible = False
            with result:
                ui.label(name).classes("text-2xl serif")
                ui.markdown(answer)

        lookup_btn.on_click(run_lookup)
        name_input.on("keydown.enter", run_lookup)

        ui.link("Back to the learning path", "/").classes("mt-6")