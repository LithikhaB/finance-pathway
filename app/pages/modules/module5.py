import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, sup, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

LESSON_INTRO = (
    "A loan is just compounding in reverse: instead of your money growing, your debt "
    "shrinks with every payment. The **EMI** (equated monthly instalment) is the fixed "
    "amount that clears a loan of *P* in *m* months at monthly rate *r*:"
)

EMI_KEY = (
    f"{var('P')} = amount borrowed, "
    f"{var('r')} = monthly rate (yearly rate ÷ 12), "
    f"{var('m')} = number of months"
)

SPLIT_NOTE = (
    "Every EMI is split into interest and principal. Early on, most of it is interest "
    "because the balance is still large; later, most of it is principal. This is why "
    "paying off a loan early saves more than it looks like: you skip mostly-interest "
    "instalments, not mostly-principal ones."
)

APR_NOTE = (
    "**Interest rate vs APR:** the quoted interest rate often excludes processing fees "
    "and other charges. APR (annual percentage rate) folds those in, so two loans with "
    "the same interest rate can have different APRs. Always compare APR, not the "
    "headline rate."
)

FINTECH_NOTE = (
    "Lending apps show 'flat rate' EMIs that look small but hide a much higher effective "
    "rate, since flat rate is charged on the original amount every year, not the shrinking "
    "balance used here. Underwriting models also use this same amortization math to check "
    "whether an EMI fits a borrower's income before approving a loan."
)

QUESTIONS = [
    {
        "q": "As a loan is repaid, the interest portion of each EMI:",
        "options": ["Stays the same every month", "Falls over time", "Rises over time"],
        "answer": 1,
        "why": "Interest is charged on the remaining balance, so as the balance shrinks, the interest portion of each EMI falls and the principal portion rises.",
    },
    {
        "q": "Two loans quote the same 10% interest rate, but Loan B has a 2% processing fee. Which is the better comparison figure?",
        "options": ["Interest rate", "APR", "EMI amount alone"],
        "answer": 1,
        "why": "APR folds in fees like processing charges, so it reflects the true annual cost. The headline interest rate alone can understate it.",
    },
    {
        "q": "A 'flat rate' EMI charges interest on:",
        "options": ["The original loan amount every year", "The shrinking balance", "Only the final month's balance"],
        "answer": 0,
        "why": "Flat rate applies the rate to the full original amount for the whole tenure, not the reducing balance, which makes the effective rate much higher than it appears.",
    },
]


def build_figure(rows: list[dict]) -> go.Figure:
    months = [r["month"] for r in rows]
    fig = go.Figure()
    fig.add_bar(x=months, y=[r["interest"] for r in rows], name="Interest", marker_color=AMBER)
    fig.add_bar(x=months, y=[r["principal"] for r in rows], name="Principal", marker_color=TEAL)
    fig.update_layout(
        barmode="stack", margin=dict(l=10, r=10, t=10, b=10), height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Month"), yaxis=dict(title="₹", tickformat=",.0f"),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def module_5() -> None:
    from app.theme import frame

    with frame():
        ui.label("5. Lending and credit").classes("text-3xl serif")
        ui.label("Every loan is compounding working against you instead of for you.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        formula(
            f"{var('EMI')} = {frac(var('P') + ' ' + var('r') + ' (1+' + var('r') + ')' + sup(var('m')), '(1+' + var('r') + ')' + sup(var('m')) + ' \u2212 1')}",
            key=EMI_KEY,
        )
        ui.markdown(SPLIT_NOTE)
        ui.markdown(APR_NOTE)

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.column().classes("w-full gap-3"):
            principal = ui.number("Loan amount (₹)", value=500000, min=1000, step=50000, format="%.0f").classes("w-full")
            rate_label = ui.label()
            rate = ui.slider(min=1, max=24, step=0.25, value=9)
            months_label = ui.label()
            months = ui.slider(min=6, max=360, step=6, value=60)

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("Monthly EMI").classes("muted text-sm")
                emi_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Total paid").classes("muted text-sm")
                total_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Total interest").classes("muted text-sm")
                interest_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_figure(calc.amortization_schedule(500000, 0.09, 60))).classes("w-full")

        def refresh() -> None:
            p, r, m = principal.value or 0, rate.value / 100, int(months.value)
            rate_label.text = f"Yearly interest rate: {rate.value}%"
            months_label.text = f"Tenure: {m} months ({m / 12:.1f} years)"
            rows = calc.amortization_schedule(p, r, m)
            payment = calc.emi(p, r, m)
            total = sum(row["payment"] for row in rows)
            emi_out.text = inr(payment)
            total_out.text = inr(total)
            interest_out.text = inr(total - p)
            chart.update_figure(build_figure(rows))

        for control in (principal, rate, months):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(5, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")