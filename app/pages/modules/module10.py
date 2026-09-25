import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

LESSON_INTRO = (
    "Fintechs make money in a few recurring shapes. A **take rate** is a cut of every "
    "transaction (a payments app keeping 1% of volume processed). **NIM (net interest "
    "margin)** is the spread a lender earns between what it pays depositors and what it "
    "charges borrowers. **Embedded finance** and **BNPL (buy now, pay later)** bolt "
    "financial products onto a non-financial app, earning fees or interest on volume "
    "they didn't have to acquire from scratch."
)

UNIT_ECON_INTRO = (
    "Whatever the model, two numbers decide whether it works: **CAC** (cost to acquire "
    "one customer) and **LTV** (lifetime value, the profit that customer generates over "
    "time). A simple estimate of LTV, assuming a constant monthly churn rate:"
)
LTV_KEY = (
    f"{var('rev')} = average revenue per customer per month, "
    f"{var('margin')} = gross margin, "
    f"{var('churn')} = monthly churn rate"
)

PAYBACK_KEY = "How many months of margin it takes to earn back what you spent acquiring the customer."

BENCHMARK_NOTE = (
    "**Rule of thumb:** an LTV:CAC ratio above 3 is generally considered healthy, below "
    "1 means you lose money on every customer, and a payback period under 12 months is "
    "usually seen as sustainable for a subscription or fee-based business."
)

FINTECH_NOTE = (
    "A BNPL provider with a thin take rate needs enormous transaction volume and low "
    "churn to make its unit economics work, since each transaction earns only a small "
    "slice. This is exactly why growth-stage fintechs obsess over CAC, churn, and "
    "payback period: get any one badly wrong and the whole model breaks."
)

QUESTIONS = [
    {
        "q": "A fintech's LTV:CAC ratio is 0.8. What does this suggest?",
        "options": [
            "The business is very healthy",
            "It is losing money on every customer it acquires",
            "The ratio has no bearing on profitability",
        ],
        "answer": 1,
        "why": "An LTV:CAC ratio below 1 means a customer generates less lifetime value than it cost to acquire them, so each new customer is a net loss.",
    },
    {
        "q": "A payments app earns a small percentage of every transaction it processes. This revenue model is a:",
        "options": ["Take rate", "Net interest margin", "Payback period"],
        "answer": 0,
        "why": "A take rate is a cut of transaction volume, exactly this kind of per-transaction revenue model, common among payment processors and marketplaces.",
    },
    {
        "q": "If a customer's CAC payback period is 18 months but the average customer churns after 10 months, this is a warning sign because:",
        "options": [
            "The customer churns before the business recovers its acquisition cost",
            "Payback period does not matter if churn is low",
            "This combination is always fine",
        ],
        "answer": 0,
        "why": "If customers leave before the business earns back what it spent acquiring them, the business never recovers its CAC, a red flag regardless of other metrics.",
    },
]


def build_unit_econ_figure(ltv: float, cac: float) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=["LTV", "CAC"], y=[ltv, cac], marker_color=[TEAL, AMBER])
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=280,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        yaxis=dict(title="₹", tickformat=",.0f"),
    )
    return fig


def module_10() -> None:
    from app.theme import frame

    with frame():
        ui.label("10. Fintech business models").classes("text-3xl serif")
        ui.label("How fintechs make money, and the two numbers that decide if it works.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        ui.markdown(UNIT_ECON_INTRO)
        formula(
            f"{var('LTV')} = {frac(var('rev') + ' \u00d7 ' + var('margin'), var('churn'))}",
            key=LTV_KEY,
        )
        formula(f"{var('Payback')} = {frac(var('CAC'), var('rev') + ' \u00d7 ' + var('margin'))}", key=PAYBACK_KEY)
        ui.markdown(BENCHMARK_NOTE)

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.row().classes("w-full gap-3 flex-wrap"):
            revenue = ui.number("Avg. revenue / customer / month (₹)", value=500, min=1, step=50, format="%.0f").classes("w-56")
            margin_label = ui.label()
            churn_label = ui.label()
        margin = ui.slider(min=10, max=90, step=5, value=60)
        churn = ui.slider(min=1, max=20, step=0.5, value=5)
        cac = ui.number("Customer acquisition cost, CAC (₹)", value=1500, min=1, step=100, format="%.0f").classes("w-56")

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("LTV").classes("muted text-sm")
                ltv_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("LTV : CAC").classes("muted text-sm")
                ratio_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Payback period").classes("muted text-sm")
                payback_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_unit_econ_figure(6000, 1500)).classes("w-full")

        def refresh() -> None:
            rev, m, ch, c = revenue.value or 1, margin.value / 100, churn.value / 100, cac.value or 1
            margin_label.text = f"Gross margin: {margin.value}%"
            churn_label.text = f"Monthly churn: {churn.value}%"
            ratio = calc.ltv_cac_ratio(rev, m, ch, c)
            ltv = ratio * c
            payback = calc.cac_payback_months(rev, m, c)
            ltv_out.text = inr(ltv)
            ratio_out.text = f"{ratio:.1f}x"
            ratio_out.style(f"color:{TEAL if ratio >= 3 else AMBER}")
            payback_out.text = f"{payback:.1f} months"
            payback_out.style(f"color:{TEAL if payback <= 12 else AMBER}")
            chart.update_figure(build_unit_econ_figure(ltv, c))

        for control in (revenue, margin, churn, cac):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(10, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")