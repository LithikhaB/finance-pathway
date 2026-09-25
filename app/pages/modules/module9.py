from nicegui import ui

from app.components.quiz import quiz
from app.theme import TEAL

LESSON_INTRO = (
    "Fintechs move other people's money, so they operate under rules designed to stop "
    "fraud, money laundering, and systemic risk. The core ones every fintech worker "
    "should recognize:"
)

RULES = [
    ("KYC (Know Your Customer)", "Verifying who a customer actually is before letting them transact, using ID and address proof."),
    ("AML (Anti-Money Laundering)", "Monitoring transactions for patterns that suggest laundering illegal money, and reporting suspicious activity."),
    ("PCI-DSS", "A security standard for anyone who stores, processes, or transmits card data, covering encryption, access control, and testing."),
    ("Data privacy laws", "Rules like GDPR or India's DPDP Act governing how personal data is collected, used, and protected."),
    ("Regulators", "Bodies like the RBI (India), SEC and FDIC (US), or FCA (UK) that license and supervise financial institutions."),
    ("Regulatory sandboxes", "Controlled environments where fintechs can test new products with real users under relaxed, closely watched rules."),
]

KYC_FLOWS = {
    "Individual": [
        ("Identity verification", "Government ID (Aadhaar, passport, driver's licence) checked against official databases."),
        ("Address proof", "A recent utility bill, bank statement, or ID with a matching address."),
        ("Risk categorization", "The customer is scored low, medium, or high risk based on profile, location, and expected activity."),
        ("Ongoing monitoring", "Transactions are watched for patterns that don't match the stated profile, triggering re-verification if needed."),
    ],
    "Business": [
        ("Entity verification", "Registration documents, tax ID, and proof the business legally exists."),
        ("Beneficial ownership", "Identifying and verifying the individuals who ultimately own or control the business, usually anyone with 25%+ ownership."),
        ("Risk categorization", "Higher-risk industries or jurisdictions (e.g. cash-intensive businesses) trigger deeper checks."),
        ("Ongoing monitoring", "Transaction patterns are reviewed continuously, with periodic re-verification of the business and its owners."),
    ],
}

FINTECH_NOTE = (
    "AML systems in production don't just follow static rules; many use machine "
    "learning to flag transactions that deviate from a customer's normal pattern. "
    "Regulatory sandboxes are how many fintechs (early UPI apps, robo-advisors) got to "
    "launch and iterate with real users before full licensing was in place."
)

QUESTIONS = [
    {
        "q": "A fintech verifies a new user's government ID before letting them open an account. This is:",
        "options": ["AML", "KYC", "PCI-DSS"],
        "answer": 1,
        "why": "KYC (Know Your Customer) is specifically about verifying who a customer is before allowing them to transact.",
    },
    {
        "q": "A payments app must encrypt stored card numbers and restrict who can access them. This requirement comes from:",
        "options": ["PCI-DSS", "GDPR", "A regulatory sandbox"],
        "answer": 0,
        "why": "PCI-DSS is the security standard specifically covering how card data must be stored, processed, and protected.",
    },
    {
        "q": "A startup wants to test a new lending product with real customers before getting a full license. It might apply to:",
        "options": ["A regulatory sandbox", "AML reporting", "KYC verification"],
        "answer": 0,
        "why": "Regulatory sandboxes let fintechs test new products with real users under relaxed, closely supervised rules, before pursuing a full license.",
    },
]


def module_9() -> None:
    from app.theme import frame

    with frame(show_calculator=False):
        ui.label("9. Regulation and compliance").classes("text-3xl serif")
        ui.label("The rules that come with the right to move other people's money.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        with ui.column().classes("w-full gap-0"):
            for name, desc in RULES:
                with ui.row().classes("module-row w-full items-start no-wrap gap-4"):
                    with ui.column().classes("gap-0 grow"):
                        ui.label(name).classes("font-medium text-lg")
                        ui.label(desc).classes("muted")

        ui.label("Trace a KYC flow").classes("text-2xl serif mt-4")
        customer_type = ui.select(list(KYC_FLOWS.keys()), value="Individual", label="Customer type").classes("w-48")
        steps_column = ui.column().classes("w-full gap-0 mt-2")

        def refresh() -> None:
            steps_column.clear()
            with steps_column:
                for i, (title, desc) in enumerate(KYC_FLOWS[customer_type.value], start=1):
                    with ui.row().classes("module-row w-full items-start no-wrap gap-4"):
                        ui.label(str(i)).classes("stat-value").style(f"color:{TEAL}; min-width:28px;")
                        with ui.column().classes("gap-0 grow"):
                            ui.label(title).classes("font-medium text-lg")
                            ui.label(desc).classes("muted")

        customer_type.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(9, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")