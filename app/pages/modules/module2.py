import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, sub, sup, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

NPV_INTRO = (
    "Cash received later is worth less than cash received today, so to compare cash "
    "flows spread over time, you discount each one back to today and add them up. "
    "This total is the **net present value (NPV)**:"
)
NPV_KEY = (
    f"{var('CF')}{sub('t')} = cash flow at time {var('t')}, "
    f"{var('r')} = discount rate, {var('t')} runs from 0 (today) to {var('n')}"
)

IRR_INTRO = (
    "The **internal rate of return (IRR)** is the discount rate that makes NPV exactly "
    "zero, the break-even return of the investment itself:"
)
IRR_KEY = "Solved by trying rates until NPV lands on zero, not by a direct formula."

DECISION_NOTE = (
    "**Decision rule:** accept a project if NPV is positive at your required rate, or "
    "equivalently if IRR is higher than that rate. The two usually agree; when they "
    "disagree (uneven cash flows, mutually exclusive projects), NPV is the more reliable one."
)

CAGR_INTRO = (
    "**CAGR** answers a simpler question: what single steady yearly growth rate gets you "
    "from a starting value to an ending value?"
)
CAGR_KEY = f"{var('n')} = number of years between the two values"

FINTECH_NOTE = (
    "A neobank deciding whether to build a new feature, a lender pricing a portfolio, or "
    "a VC valuing a fintech startup all reduce the decision to the same question: what is "
    "this future stream of cash worth today? NPV and IRR are that question in formula form."
)

QUESTIONS = [
    {
        "q": "You invest ₹100 today and get back ₹110 in one year. At a 10% discount rate, the NPV is:",
        "options": ["Positive", "Zero", "Negative"],
        "answer": 1,
        "why": "110 discounted at 10% for one year is exactly 100, so NPV = -100 + 100 = 0. The 10% rate is also this investment's IRR.",
    },
    {
        "q": "A project's IRR is 15% and your required rate is 12%. Should you accept it, all else equal?",
        "options": ["Yes, IRR exceeds the required rate", "No, IRR is too low", "Cannot tell from IRR alone"],
        "answer": 0,
        "why": "When IRR is above your required (hurdle) rate, the project's NPV at that hurdle rate is positive, so it clears the bar.",
    },
    {
        "q": "A fund grows from ₹100 to ₹200 over 5 years. Its CAGR is closest to:",
        "options": ["20% a year", "About 14.9% a year", "100% a year"],
        "answer": 1,
        "why": "CAGR = (200/100)^(1/5) - 1 ≈ 14.9%. Dividing the total 100% gain by 5 years (20%) ignores compounding and overstates it.",
    },
]


def build_cashflow_figure(flows: list[float], rate: float) -> go.Figure:
    years = list(range(len(flows)))
    discounted = [cf / (1 + rate) ** t for t, cf in enumerate(flows)]
    fig = go.Figure()
    fig.add_bar(x=years, y=flows, name="Cash flow", marker_color=MUTED)
    fig.add_bar(x=years, y=discounted, name="Discounted to today", marker_color=TEAL)
    fig.update_layout(
        barmode="group", margin=dict(l=10, r=10, t=10, b=10), height=300,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Year", dtick=1), yaxis=dict(title="₹", tickformat=",.0f"),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def module_2() -> None:
    from app.theme import frame

    with frame():
        ui.label("2. Cash flows and valuation").classes("text-3xl serif")
        ui.label("How to compare money that arrives at different times.").classes("muted text-lg")

        ui.markdown(NPV_INTRO)
        formula(
            f"{var('NPV')} = \u03a3 {frac(var('CF') + sub('t'), '(1 + ' + var('r') + ')' + sup(var('t')))}",
            key=NPV_KEY,
        )
        ui.markdown(IRR_INTRO)
        formula(f"{var('NPV')}({var('IRR')}) = 0", key=IRR_KEY)
        ui.markdown(DECISION_NOTE)

        ui.label("Try it: NPV and IRR").classes("text-2xl serif mt-4")
        ui.label("Enter an initial outlay (negative) and up to four yearly cash flows.").classes("muted")
        with ui.row().classes("w-full gap-3 flex-wrap"):
            cf0 = ui.number("Year 0 (₹)", value=-100000, step=10000, format="%.0f").classes("w-32")
            cf1 = ui.number("Year 1 (₹)", value=30000, step=5000, format="%.0f").classes("w-32")
            cf2 = ui.number("Year 2 (₹)", value=35000, step=5000, format="%.0f").classes("w-32")
            cf3 = ui.number("Year 3 (₹)", value=40000, step=5000, format="%.0f").classes("w-32")
            cf4 = ui.number("Year 4 (₹)", value=45000, step=5000, format="%.0f").classes("w-32")
        rate_label = ui.label()
        rate = ui.slider(min=1, max=30, step=0.5, value=10)

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("NPV at this rate").classes("muted text-sm")
                npv_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("IRR").classes("muted text-sm")
                irr_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Decision").classes("muted text-sm")
                decision_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_cashflow_figure([-100000, 30000, 35000, 40000, 45000], 0.10)).classes("w-full")

        def refresh() -> None:
            flows = [cf0.value or 0, cf1.value or 0, cf2.value or 0, cf3.value or 0, cf4.value or 0]
            r = rate.value / 100
            rate_label.text = f"Discount rate: {rate.value}%"
            npv_value = calc.npv(r, flows)
            npv_out.text = inr(npv_value)
            try:
                irr_out.text = pct(calc.irr(flows))
            except ValueError:
                irr_out.text = "Not found"
            decision_out.text = "Accept" if npv_value > 0 else "Reject"
            decision_out.style(f"color:{TEAL if npv_value > 0 else AMBER}")
            chart.update_figure(build_cashflow_figure(flows, r))

        for control in (cf0, cf1, cf2, cf3, cf4, rate):
            control.on_value_change(refresh)
        refresh()

        ui.label("Try it: CAGR").classes("text-2xl serif mt-4")
        ui.markdown(CAGR_INTRO)
        formula(
            f"{var('CAGR')} = {frac(var('End'), var('Begin'))}{sup('1/' + var('n'))} \u2212 1",
            key=CAGR_KEY,
        )
        with ui.row().classes("w-full gap-3 flex-wrap items-end"):
            begin = ui.number("Starting value (₹)", value=100000, min=1, step=10000, format="%.0f").classes("w-40")
            end = ui.number("Ending value (₹)", value=180000, min=1, step=10000, format="%.0f").classes("w-40")
            years_n = ui.number("Years", value=5, min=1, step=1, format="%.0f").classes("w-24")
            cagr_out = ui.label().classes("stat-value")

        def refresh_cagr() -> None:
            try:
                cagr_out.text = pct(calc.cagr(begin.value or 1, end.value or 1, years_n.value or 1))
            except ValueError:
                cagr_out.text = "Enter positive values"

        for control in (begin, end, years_n):
            control.on_value_change(refresh_cagr)
        refresh_cagr()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(2, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")