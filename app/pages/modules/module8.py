import math

import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, var
from app.components.quiz import quiz
from app.format import inr
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

LESSON_INTRO = (
    "Every financial institution manages the same handful of risks, just wearing "
    "different names:"
)

RISK_TYPES = [
    ("Credit risk", "A borrower fails to repay a loan or a counterparty defaults on an obligation."),
    ("Market risk", "The value of investments falls because prices, rates, or currencies move against you."),
    ("Liquidity risk", "You can't meet short-term obligations, even if you're solvent on paper, because cash isn't available when needed."),
    ("Operational risk", "Losses from failed processes, systems, or people: a bug, an outage, an employee error."),
    ("Fraud risk", "Losses from deliberate deception: stolen cards, fake identities, account takeover."),
]

VAR_INTRO = (
    "**Value at Risk (VaR)** puts a single number on market risk: the loss you would not "
    "expect to exceed, at a given confidence level, over a given time horizon. A 95% "
    "1-day VaR of ₹1,00,000 means a bigger loss than that is expected only about 1 day in 20."
)
VAR_KEY = (
    f"{var('z')} = confidence multiplier (higher confidence needs a bigger multiplier), "
    f"{var('sigma')} = daily volatility, {var('t')} = number of days, "
    f"{var('V')} = portfolio value"
)

FINTECH_NOTE = (
    "Banks hold regulatory capital sized using VaR-like models, so a bad day doesn't "
    "wipe them out. Fraud systems score every transaction in milliseconds for exactly "
    "this reason: catching fraud risk before it becomes a realized loss is far cheaper "
    "than absorbing it afterward."
)

QUESTIONS = [
    {
        "q": "A UPI app suffers a two-hour outage due to a software bug, causing failed payments. This is an example of:",
        "options": ["Credit risk", "Operational risk", "Market risk"],
        "answer": 1,
        "why": "A system failure from a bug or outage is operational risk: a loss caused by failed internal processes or systems, not by a borrower defaulting or prices moving.",
    },
    {
        "q": "A bank is solvent, but can't meet a sudden wave of withdrawal requests because its cash is tied up in long-term loans. This is:",
        "options": ["Liquidity risk", "Fraud risk", "Credit risk"],
        "answer": 0,
        "why": "Liquidity risk is the inability to meet short-term obligations even when the institution is solvent overall, because cash isn't available exactly when it's needed.",
    },
    {
        "q": "A portfolio's 95% 1-day VaR is ₹50,000. This means:",
        "options": [
            "The portfolio will never lose more than ₹50,000",
            "A loss beyond ₹50,000 in a single day is expected only about 5% of the time",
            "The portfolio is guaranteed to lose ₹50,000",
        ],
        "answer": 1,
        "why": "VaR is a confidence-level statement, not a guarantee: it estimates that a loss beyond the VaR figure should happen only about 5% of trading days, not that it can never happen.",
    },
]


def build_var_figure(daily_volatility: float, confidence: float) -> go.Figure:
    z_scores = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}
    z = z_scores[confidence]
    xs = [i / 20 for i in range(-80, 81)]  # -4 to 4 standard deviations
    ys = [math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi) for x in xs]
    fig = go.Figure()
    fig.add_scatter(x=xs, y=ys, name="Return distribution", line=dict(color=MUTED, width=2), fill="tozeroy",
                    fillcolor="rgba(91,103,120,0.10)")
    tail_x = [x for x in xs if x <= -z]
    tail_y = [math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi) for x in tail_x]
    fig.add_scatter(x=tail_x, y=tail_y, name=f"Worst {int((1 - confidence) * 100)}%", line=dict(color=AMBER, width=2),
                    fill="tozeroy", fillcolor="rgba(180,83,9,0.35)")
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=260,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Standard deviations from average return", zeroline=False),
        yaxis=dict(visible=False),
        legend=dict(orientation="h", y=-0.3),
    )
    return fig


def module_8() -> None:
    from app.theme import frame

    with frame():
        ui.label("8. Risk management").classes("text-3xl serif")
        ui.label("The handful of risks every financial institution has to manage.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        with ui.column().classes("w-full gap-0"):
            for name, desc in RISK_TYPES:
                with ui.row().classes("module-row w-full items-start no-wrap gap-4"):
                    with ui.column().classes("gap-0 grow"):
                        ui.label(name).classes("font-medium text-lg")
                        ui.label(desc).classes("muted")

        ui.markdown(VAR_INTRO).classes("mt-4")
        formula(f"{var('VaR')} = {var('V')} \u00d7 {var('sigma')} \u00d7 {var('z')} \u00d7 \u221a{var('t')}", key=VAR_KEY)

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.row().classes("w-full gap-3 flex-wrap"):
            value = ui.number("Portfolio value (₹)", value=1000000, min=0, step=100000, format="%.0f").classes("w-48")
            vol_label = ui.label()
        vol = ui.slider(min=0.5, max=5, step=0.1, value=2)
        with ui.row().classes("gap-4 items-end"):
            confidence = ui.select({0.90: "90%", 0.95: "95%", 0.99: "99%"}, value=0.95, label="Confidence").classes("w-32")
            days = ui.number("Horizon (days)", value=1, min=1, step=1, format="%.0f").classes("w-32")

        with ui.column().classes("gap-0"):
            ui.label("Value at Risk").classes("muted text-sm")
            var_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_var_figure(0.02, 0.95)).classes("w-full")

        def refresh() -> None:
            v, sigma, conf, d = value.value or 0, vol.value / 100, confidence.value, int(days.value or 1)
            vol_label.text = f"Daily volatility: {vol.value}%"
            var_out.text = inr(calc.value_at_risk(v, sigma, conf, d))
            chart.update_figure(build_var_figure(sigma, conf))

        for control in (value, vol, confidence, days):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(8, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")