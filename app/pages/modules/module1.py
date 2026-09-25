import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, sup, times, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL, frame
from core import calculations as calc

FREQUENCIES = {1: "Yearly", 4: "Quarterly", 12: "Monthly", 365: "Daily"}

LESSON_INTRO = (
    "**Compounding** means you earn interest on your earlier interest. "
    "The balance after *t* years is:"
)

FV_KEY = (
    f"{var('P')} = amount you put in, "
    f"{var('r')} = yearly rate, "
    f"{var('n')} = times compounded per year, "
    f"{var('t')} = years"
)

EAR_INTRO = (
    'Because "12% a year" means different things depending on how often it compounds, '
    'lenders and banks quote the **effective annual rate (EAR)**, what you actually earn '
    "or pay in a year:"
)

EAR_KEY = "A 12% rate compounded monthly has an EAR of about 12.68%, not 12%."

REAL_INTRO = (
    "**Inflation** shrinks what money can buy. Your **real return** compares your rate "
    "against rising prices:"
)

REAL_KEY = (
    "Not simply nominal minus inflation. A saver earning 6% when prices rise 5% "
    "gains only about 0.95% in real buying power."
)

FINTECH_NOTE = (
    "Every savings app, loan offer and credit card statement runs on this formula. "
    "When a lending app shows a 'flat' rate versus an 'effective' rate, this is the "
    "difference. Rate disclosure rules exist because compounding frequency can hide the true cost."
)

QUESTIONS = [
    {
        "q": "You invest ₹10,000 at 10% a year, compounded yearly. What is it worth after 2 years?",
        "options": ["₹12,000", "₹12,100", "₹11,000"],
        "answer": 1,
        "why": "Year 2 earns interest on year 1's interest: 10,000 × 1.1 × 1.1 = 12,100. Simple interest would give 12,000.",
    },
    {
        "q": "A loan quotes 12% a year compounded monthly. Its effective annual rate is:",
        "options": ["Exactly 12%", "About 12.68%", "About 14%"],
        "answer": 1,
        "why": "EAR = (1 + 0.12/12)^12 - 1 ≈ 12.68%. More frequent compounding always raises the effective rate.",
    },
    {
        "q": "A deposit pays 6% while inflation is 5%. Your real return is roughly:",
        "options": ["6%", "11%", "About 0.95%"],
        "answer": 2,
        "why": "Real return = 1.06 / 1.05 - 1 ≈ 0.95%. Most of the interest only keeps pace with prices.",
    },
]


def growth_series(principal: float, rate: float, years: int, n: int, inflation: float):
    """Yearly balances: nominal, and adjusted to today's buying power."""
    xs = list(range(years + 1))
    nominal = [calc.compound_interest(principal, rate, t, n) for t in xs]
    real = [calc.present_value(v, inflation, t) for t, v in zip(xs, nominal)]
    return xs, nominal, real


def build_figure(principal, rate, years, n, inflation) -> go.Figure:
    xs, nominal, real = growth_series(principal, rate, years, n, inflation)
    fig = go.Figure()
    fig.add_scatter(x=xs, y=[principal] * len(xs), name="Amount you put in",
                    line=dict(color=MUTED, dash="dash"))
    fig.add_scatter(x=xs, y=real, name="In today's buying power", line=dict(color=AMBER, width=3))
    fig.add_scatter(x=xs, y=nominal, name="Balance", line=dict(color=TEAL, width=3))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=340, hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Years", dtick=max(1, years // 10)),
        yaxis=dict(title="₹", tickformat=",.0f"),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def module_1() -> None:
    with frame():
        ui.label("1. Time value of money").classes("text-3xl serif")
        ui.label("A rupee today is worth more than a rupee later. Here is by how much.").classes(
            "muted text-lg"
        )

        ui.markdown(LESSON_INTRO)
        formula(
            f"{var('FV')} = {var('P')} (1 + {frac('r', 'n')}){sup(var('n') + times() + var('t'))}",
            key=FV_KEY,
        )

        ui.markdown(EAR_INTRO)
        formula(
            f"{var('EAR')} = (1 + {frac('r', 'n')}){sup(var('n'))} \u2212 1",
            key=EAR_KEY,
        )

        ui.markdown(REAL_INTRO)
        formula(
            f"1 + {var('real')} = {frac('1 + ' + var('nominal'), '1 + ' + var('inflation'))}",
            key=REAL_KEY,
        )

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.column().classes("w-full gap-3"):
            principal = ui.number("Amount invested (₹)", value=100000, min=0, step=10000, format="%.0f").classes("w-full")
            rate_label = ui.label()
            rate = ui.slider(min=0, max=20, step=0.5, value=8)
            years_label = ui.label()
            years = ui.slider(min=1, max=40, step=1, value=20)
            infl_label = ui.label()
            infl = ui.slider(min=0, max=12, step=0.5, value=5)
            freq = ui.select(FREQUENCIES, value=12, label="Interest added").classes("w-full")

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("Balance at the end").classes("muted text-sm")
                fv_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Effective annual rate").classes("muted text-sm")
                ear_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Worth in today's money").classes("muted text-sm")
                real_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_figure(100000, 0.08, 20, 12, 0.05)).classes("w-full")

        def refresh() -> None:
            p = principal.value or 0
            r, y, i, n = rate.value / 100, int(years.value), infl.value / 100, freq.value
            rate_label.text = f"Yearly interest rate: {rate.value}%"
            years_label.text = f"Years: {y}"
            infl_label.text = f"Yearly inflation: {infl.value}%"
            fv = calc.compound_interest(p, r, y, n)
            fv_out.text = inr(fv)
            ear_out.text = pct(calc.effective_annual_rate(r, n))
            real_out.text = inr(calc.present_value(fv, i, y))
            chart.update_figure(build_figure(p, r, y, n, i))

        for control in (principal, rate, years, infl, freq):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(1, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")