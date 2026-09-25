from nicegui import ui

from app.components.quiz import quiz
from app.format import inr
from app.theme import AMBER, MUTED, RULE, TEAL

ACCOUNTS = ["Cash", "Loans Receivable", "Customer Deposits", "Equity", "Interest Income"]

LESSON_INTRO = (
    "A bank account is really just a row in a **ledger**: a record of what is owed to "
    "whom. Every entry in double-entry bookkeeping touches two accounts at once, a "
    "**debit** and a **credit** of the same amount, so the books always balance: "
    "**assets = liabilities + equity**. Nothing is ever recorded only once."
)

RECONCILIATION_NOTE = (
    "**Reconciliation** is the process of checking that a bank's internal ledger matches "
    "reality: the cash it thinks it holds against the cash actually in its accounts, or a "
    "payment processor's records against the bank's. A mismatch usually means a "
    "transaction was missed, duplicated, or is still in transit."
)

FINTECH_NOTE = (
    "Every fintech ledger, from a UPI wallet to a lending book, is built on this same "
    "principle: nothing moves without an equal and opposite entry. This is what lets "
    "auditors and regulators verify a fintech's books, and why 'the numbers don't "
    "reconcile' is treated as a serious incident, not a rounding error."
)

PRESETS = [
    ("Customer deposits ₹10,000", "Cash", "Customer Deposits", 10000),
    ("Bank lends ₹5,000 to a customer", "Loans Receivable", "Cash", 5000),
    ("Customer repays ₹500 with ₹50 interest", "Cash", "Loans Receivable", 500),
    ("Owner invests ₹20,000 in the bank", "Cash", "Equity", 20000),
]

QUESTIONS = [
    {
        "q": "A customer deposits ₹1,000 in cash. Which entry is correct?",
        "options": [
            "Debit Cash ₹1,000, credit Customer Deposits ₹1,000",
            "Debit Cash ₹1,000 only",
            "Credit Cash ₹1,000, credit Customer Deposits ₹1,000",
        ],
        "answer": 0,
        "why": "The bank's cash increases (debit) and it now owes the customer that amount (credit to Customer Deposits, a liability). Every entry needs both a debit and a credit.",
    },
    {
        "q": "In double-entry bookkeeping, total debits across all accounts should:",
        "options": ["Always equal total credits", "Always exceed total credits", "Have no fixed relationship to credits"],
        "answer": 0,
        "why": "Every transaction records equal debit and credit amounts, so summed across all accounts, total debits always equal total credits. This equality is the basic error-check of the whole system.",
    },
    {
        "q": "A payment processor's records show ₹50,000 collected, but the bank shows only ₹48,000 received. This gap is found by:",
        "options": ["Reconciliation", "Underwriting", "Amortization"],
        "answer": 0,
        "why": "Reconciliation is exactly the process of comparing two records of the same activity to find and explain differences like this one.",
    },
]


def module_3() -> None:
    from app.theme import frame

    with frame(show_calculator=False):
        ui.label("3. Banking and ledgers").classes("text-3xl serif")
        ui.label("Every account is a ledger entry, and every entry has two sides.").classes("muted text-lg")

        ui.markdown(LESSON_INTRO)
        ui.markdown(RECONCILIATION_NOTE)

        ui.label("Try it: post a transaction").classes("text-2xl serif mt-4")
        ui.label("Every transaction needs a debit account and a credit account of equal amount.").classes("muted")

        transactions: list[dict] = []
        table = ui.table(
            columns=[
                {"name": "desc", "label": "Transaction", "field": "desc", "align": "left"},
                {"name": "debit_acc", "label": "Debit", "field": "debit_acc", "align": "left"},
                {"name": "credit_acc", "label": "Credit", "field": "credit_acc", "align": "left"},
                {"name": "amount", "label": "Amount", "field": "amount", "align": "right"},
            ],
            rows=[], row_key="desc",
        ).classes("w-full")

        balances_row = ui.row().classes("w-full gap-6 flex-wrap mt-2")
        check_label = ui.label().classes("mt-2 font-medium")

        def refresh() -> None:
            table.rows = [
                {**t, "amount": inr(t["amount"])} for t in transactions
            ]
            table.update()
            debit_totals = {a: 0.0 for a in ACCOUNTS}
            credit_totals = {a: 0.0 for a in ACCOUNTS}
            for t in transactions:
                debit_totals[t["debit_acc"]] += t["amount"]
                credit_totals[t["credit_acc"]] += t["amount"]
            balances_row.clear()
            with balances_row:
                for a in ACCOUNTS:
                    net = debit_totals[a] - credit_totals[a]
                    with ui.column().classes("gap-0"):
                        ui.label(a).classes("muted text-sm")
                        ui.label(inr(net)).classes("stat-value").style(
                            f"color:{TEAL if net >= 0 else AMBER}"
                        )
            total_debits = sum(debit_totals.values())
            total_credits = sum(credit_totals.values())
            check_label.text = (
                f"Total debits {inr(total_debits)} = total credits {inr(total_credits)}, books balance."
                if abs(total_debits - total_credits) < 0.01
                else f"Out of balance: debits {inr(total_debits)} vs credits {inr(total_credits)}."
            )
            check_label.style(f"color:{TEAL if abs(total_debits - total_credits) < 0.01 else AMBER}")

        def post(desc: str, debit_acc: str, credit_acc: str, amount: float) -> None:
            if debit_acc == credit_acc:
                ui.notify("Debit and credit accounts must differ.", type="warning")
                return
            if amount <= 0:
                ui.notify("Amount must be positive.", type="warning")
                return
            transactions.append({"desc": desc, "debit_acc": debit_acc, "credit_acc": credit_acc, "amount": amount})
            refresh()

        with ui.row().classes("gap-2 flex-wrap"):
            for label, debit_acc, credit_acc, amount in PRESETS:
                ui.button(label, on_click=lambda l=label, d=debit_acc, c=credit_acc, a=amount: post(l, d, c, a)).props(
                    "outline dense"
                )

        with ui.row().classes("w-full gap-3 flex-wrap items-end mt-2"):
            desc_in = ui.input("Description", value="Custom transaction").classes("w-56")
            debit_sel = ui.select(ACCOUNTS, value=ACCOUNTS[0], label="Debit account").classes("w-48")
            credit_sel = ui.select(ACCOUNTS, value=ACCOUNTS[1], label="Credit account").classes("w-48")
            amount_in = ui.number("Amount (₹)", value=1000, min=1, step=100, format="%.0f").classes("w-32")
            ui.button(
                "Post", on_click=lambda: post(desc_in.value, debit_sel.value, credit_sel.value, amount_in.value or 0)
            )
            ui.button(
                "Reset ledger",
                on_click=lambda: (transactions.clear(), refresh()),
            ).props("flat")

        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(3, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")