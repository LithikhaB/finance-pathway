import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, sup, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

LESSON_INTRO = (
    "**Risk and return move together.** A bank deposit is safe but pays little; equities "
    "can grow faster but can also fall. **Diversification**, spreading money across many "
    "assets, doesn't raise your return, but it reduces the chance that one bad outcome "
    "wipes you out."
)

SIP_INTRO = (
    "A **SIP (systematic investment plan)** invests a fixed amount every month rather "
    "than all at once, so you buy at many different prices over time. Its future value "
    "compounds like a series of small deposits:"
)
SIP_KEY = (
    f"{var('A')} = amount invested each month, "
    f"{var('i')} = monthly rate (yearly rate \u00f7 12), "
    f"{var('m')} = number of months"
)

ALLOCATION_NOTE = (
    "**Asset allocation** is the mix of stocks, bonds, and cash you hold, and it matters "
    "more to long-run returns than picking individual stocks. Younger investors with a "
    "longer horizon can typically hold more equities, since they have time to ride out "
    "downturns; those closer to a goal shift toward safer assets."
)

FINTECH_NOTE = (
    "Robo-advisors automate exactly this: they ask a few questions to gauge your risk "
    "tolerance and time horizon, then run this same compounding math to set an asset "
    "mix and periodically rebalance it, all without a human advisor in the loop."
)

QUESTIONS = [
    {
        "q": "Diversifying across many stocks instead of holding just one mainly:",
        "options": ["Guarantees a higher return", "Reduces the risk from any single investment", "Eliminates all risk"],
        "answer": 1,
        "why": "Diversification spreads risk so that one company's bad outcome doesn't sink the whole portfolio, but it doesn't raise expected return or remove market-wide risk.",
    },
    {
        "q": "A 25-year-old and a 60-year-old both save for retirement. Who typically holds more equities?",
        "options": ["The 25-year-old, with more time to recover from downturns", "The 60-year-old, for higher growth", "Both should hold identical allocations"],
        "answer": 0,
        "why": "A longer time horizon lets younger investors ride out short-term volatility, so they can typically afford a higher allocation to equities than someone near retirement.",
    },
    {
        "q": "Compared to investing a lump sum today, a monthly SIP:",
        "options": ["Always earns a higher return", "Spreads purchases across many prices over time", "Removes market risk entirely"],
        "answer": 1,
        "why": "A SIP buys at many different prices over time (rupee-cost averaging), which smooths out timing risk, but it doesn't guarantee a higher return or remove market risk.",
    },
]


def build_sip_figure(monthly: float, rate: float, years: int) -> go.Figure:
    months_list = list(range(0, years * 12 + 1, 12))
    invested = [monthly * m for m in months_list]
    value = [calc.sip_future_value(monthly, rate, m) for m in months_list]
    fig = go.Figure()
    fig.add_scatter(x=[m // 12 for m in months_list], y=invested, name="Amount invested",
                    line=dict(color=MUTED, dash="dash"))
    fig.add_scatter(x=[m // 12 for m in months_list], y=value, name="Portfolio value",
                    line=dict(color=TEAL, width=3))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=320, hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Years"), yaxis=dict(title="₹", tickformat=",.0f"),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def module_7() -> None:
    from app.theme import frame

    with frame():
        ui.label("7. Investing and portfolios").classes("text-3xl serif")
        ui.label("Risk, return, and the discipline of investing a little every month.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        ui.markdown(SIP_INTRO)
        formula(
            f"{var('FV')} = {var('A')} \u00d7 {frac('(1+' + var('i') + ')' + sup(var('m')) + ' \u2212 1', var('i'))}",
            key=SIP_KEY,
        )
        ui.markdown(ALLOCATION_NOTE)

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.column().classes("w-full gap-3"):
            monthly = ui.number("Monthly investment (₹)", value=5000, min=0, step=500, format="%.0f").classes("w-full")
            rate_label = ui.label()
            rate = ui.slider(min=1, max=20, step=0.5, value=12)
            years_label = ui.label()
            years = ui.slider(min=1, max=35, step=1, value=15)

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("Amount invested").classes("muted text-sm")
                invested_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Portfolio value").classes("muted text-sm")
                value_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Growth from returns").classes("muted text-sm")
                gain_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_sip_figure(5000, 0.12, 15)).classes("w-full")

        def refresh() -> None:
            m, r, y = monthly.value or 0, rate.value / 100, int(years.value)
            rate_label.text = f"Expected yearly return: {rate.value}%"
            years_label.text = f"Years: {y}"
            months = y * 12
            invested = m * months
            value = calc.sip_future_value(m, r, months)
            invested_out.text = inr(invested)
            value_out.text = inr(value)
            gain_out.text = inr(value - invested)
            chart.update_figure(build_sip_figure(m, r, y))

        for control in (monthly, rate, years):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(7, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")