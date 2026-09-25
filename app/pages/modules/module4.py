from nicegui import ui

from app.components.quiz import quiz
from app.theme import TEAL

LESSON_INTRO = (
    "Every payment method moves money through the same three stages, just at "
    "different speeds: **authorization** (the payer's bank confirms funds and approves "
    "it), **clearing** (banks exchange payment instructions and agree what is owed), and "
    "**settlement** (money actually moves between banks). What you see as 'paid' is "
    "usually only the first stage."
)

RAILS = {
    "Card payment": {
        "fee_note": "Merchant pays an interchange fee, typically 1 to 3 percent of the transaction.",
        "steps": [
            ("Authorization", "Seconds", "Your bank checks funds and holds the amount. The merchant sees 'approved'."),
            ("Clearing", "Same day to next day", "Card networks batch the transaction and pass it to your bank for confirmation."),
            ("Settlement", "1 to 2 business days", "Your bank transfers the actual funds to the merchant's bank."),
        ],
    },
    "UPI": {
        "fee_note": "Usually free for the payer; merchants may pay a small fee or none, depending on the country.",
        "steps": [
            ("Authorization", "Seconds", "Your bank verifies your PIN and available balance instantly."),
            ("Clearing", "Seconds", "The instruction routes through a shared real-time network to the receiving bank."),
            ("Settlement", "Seconds to minutes", "Funds move between banks almost immediately, unusually fast for a bank transfer."),
        ],
    },
    "Wire / SWIFT": {
        "fee_note": "Often a flat fee of ₹500 to ₹2,000 or more, especially for cross-border transfers.",
        "steps": [
            ("Authorization", "Minutes", "Your bank verifies the instruction and available funds, often with manual checks."),
            ("Clearing", "Hours", "Instructions pass through one or more correspondent banks, especially across borders."),
            ("Settlement", "1 to 5 business days", "Funds finally reach the receiving bank, slower the more intermediaries are involved."),
        ],
    },
}

FINTECH_NOTE = (
    "A 'pending' transaction in your banking app is money that has been authorized but "
    "not yet settled. Fintechs that promise instant transfers usually front the money "
    "themselves and collect it from the real settlement later, taking on settlement risk "
    "so you don't have to wait."
)

QUESTIONS = [
    {
        "q": "A payment app shows your transaction as 'approved' the instant you pay. This means:",
        "options": ["The money has fully settled", "The payment was authorized, settlement may still be pending", "The transaction was reversed"],
        "answer": 1,
        "why": "Authorization confirms funds and approves the payment instantly, but the actual movement of money (settlement) can take longer depending on the rail.",
    },
    {
        "q": "Which payment rail typically settles the fastest?",
        "options": ["Wire / SWIFT", "UPI", "Card payment"],
        "answer": 1,
        "why": "UPI runs on a real-time network built for near-instant settlement between banks, unlike card networks or wires, which involve batching or correspondent banks.",
    },
    {
        "q": "Cross-border wires are often slower than domestic ones mainly because:",
        "options": [
            "They use a different currency, which always takes longer",
            "They usually pass through one or more correspondent banks",
            "Banks intentionally delay international transfers",
        ],
        "answer": 1,
        "why": "Cross-border wires often route through correspondent banks that relay the payment onward, and each additional hop adds processing time.",
    },
]


def module_4() -> None:
    from app.theme import frame

    with frame(show_calculator=False):
        ui.label("4. Payments").classes("text-3xl serif")
        ui.label("Authorization, clearing, and settlement, at very different speeds.").classes("muted text-lg")

        ui.markdown(LESSON_INTRO)

        ui.label("Trace a payment").classes("text-2xl serif mt-4")
        method = ui.select(list(RAILS.keys()), value="Card payment", label="Payment method").classes("w-56")
        fee_label = ui.label().classes("muted")
        steps_column = ui.column().classes("w-full gap-0 mt-2")

        def refresh() -> None:
            info = RAILS[method.value]
            fee_label.text = info["fee_note"]
            steps_column.clear()
            with steps_column:
                for i, (title, timing, desc) in enumerate(info["steps"], start=1):
                    with ui.row().classes("module-row w-full items-start no-wrap gap-4"):
                        ui.label(str(i)).classes("stat-value").style(f"color:{TEAL}; min-width:28px;")
                        with ui.column().classes("gap-0 grow"):
                            with ui.row().classes("items-baseline gap-2"):
                                ui.label(title).classes("font-medium text-lg")
                                ui.label(f"\u2022 {timing}").classes("muted text-sm")
                            ui.label(desc).classes("muted")

        method.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(4, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")