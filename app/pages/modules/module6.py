import plotly.graph_objects as go
from nicegui import ui

from app.components.formula import formula, frac, sub, sup, var
from app.components.quiz import quiz
from app.format import inr, pct
from app.theme import AMBER, INK, MUTED, TEAL
from core import calculations as calc

LESSON_INTRO = (
    "**Equities** are ownership: a share's value depends on the company's future profits, "
    "with no promised payback. **Bonds** are a loan: the issuer promises fixed coupon "
    "payments and the face value back at maturity. A bond's price is the present value of "
    "those promised payments:"
)
BOND_KEY = (
    f"{var('coupon')} = periodic interest payment, "
    f"{var('y')} = market yield per period, "
    f"{var('n')} = number of payments left, "
    f"{var('face')} = amount repaid at maturity"
)

RELATIONSHIP_NOTE = (
    "**Bond prices and yields move opposite ways.** When market yields rise, existing "
    "bonds with lower fixed coupons become less attractive, so their price falls to "
    "compensate; when yields fall, existing bonds become more valuable. A bond priced "
    "above face value is at a **premium**, below face value at a **discount**, and at "
    "face value it is trading **at par** (coupon rate equals yield)."
)

OTHER_INSTRUMENTS = (
    "**Mutual funds and ETFs** pool many investors' money into a basket of stocks or "
    "bonds, so one purchase buys diversification. **Derivatives** (futures, options) "
    "derive their value from an underlying asset and are mainly used to hedge risk or "
    "speculate on price moves, not to raise funds directly."
)

SETTLEMENT_NOTE = (
    "**Order lifecycle:** an order is placed, matched with a counterparty, executed at a "
    "price, and then settled, when cash and securities actually change hands. Most "
    "markets settle T+1 (one business day after the trade), which is why your brokerage "
    "app can show a trade as 'done' before the money has technically moved."
)

FINTECH_NOTE = (
    "Robo-advisors and trading apps price and rank bonds by yield, and their risk "
    "warnings about 'interest rate risk' are exactly this inverse price-yield "
    "relationship. Settlement cycles (T+1) also drive how fast an app can let you "
    "withdraw proceeds from a sale."
)

QUESTIONS = [
    {
        "q": "Market yields rise sharply after you buy a bond. Its market price will likely:",
        "options": ["Rise", "Fall", "Stay exactly the same"],
        "answer": 1,
        "why": "Bond prices and yields move inversely: as new bonds offer higher yields, your older, lower-coupon bond becomes less attractive and its price falls.",
    },
    {
        "q": "A bond's coupon rate equals the current market yield. The bond trades:",
        "options": ["At a premium", "At a discount", "At par"],
        "answer": 2,
        "why": "When the coupon rate matches the yield investors demand, the present value of its payments equals its face value, so it trades at par.",
    },
    {
        "q": "'T+1 settlement' means:",
        "options": ["The trade completes instantly", "Cash and securities exchange one business day after the trade", "The trade is cancelled after one day"],
        "answer": 1,
        "why": "T+1 means settlement, the actual exchange of cash and securities, happens one business day after the trade date, even though the trade itself executed immediately.",
    },
]


def build_price_yield_figure(face: float, coupon_rate: float, years: int, freq: int, current_yield: float) -> go.Figure:
    yields = [y / 1000 for y in range(5, 201, 5)]  # 0.5% to 20%
    prices = [calc.bond_price(face, coupon_rate, y, years, freq) for y in yields]
    current_price = calc.bond_price(face, coupon_rate, current_yield, years, freq)
    fig = go.Figure()
    fig.add_scatter(x=[y * 100 for y in yields], y=prices, name="Price", line=dict(color=TEAL, width=3))
    fig.add_scatter(x=[current_yield * 100], y=[current_price], mode="markers", name="Current yield",
                    marker=dict(color=AMBER, size=11))
    fig.add_hline(y=face, line=dict(color=MUTED, dash="dash"), annotation_text="Face value")
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=INK),
        xaxis=dict(title="Market yield (%)"), yaxis=dict(title="Price (₹)", tickformat=",.0f"),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def module_6() -> None:
    from app.theme import frame

    with frame():
        ui.label("6. Capital markets").classes("text-3xl serif")
        ui.label("How stocks, bonds, funds and derivatives are priced and traded.").classes("muted text-lg")

        ui.markdown(LESSON_INTRO)
        formula(
            f"{var('Price')} = \u03a3 {frac(var('coupon'), '(1 + ' + var('y') + ')' + sup(var('t')))}"
            f" + {frac(var('face'), '(1 + ' + var('y') + ')' + sup(var('n')))}",
            key=BOND_KEY,
        )
        ui.markdown(RELATIONSHIP_NOTE)
        ui.markdown(OTHER_INSTRUMENTS)
        ui.markdown(SETTLEMENT_NOTE)

        ui.label("Try it").classes("text-2xl serif mt-4")
        with ui.row().classes("w-full gap-3 flex-wrap"):
            face = ui.number("Face value (₹)", value=1000, min=1, step=100, format="%.0f").classes("w-32")
            coupon_label = ui.label()
            years_lbl = ui.label()
        coupon = ui.slider(min=0, max=15, step=0.25, value=6)
        years = ui.slider(min=1, max=30, step=1, value=10)
        yield_label = ui.label()
        ytm = ui.slider(min=0.5, max=20, step=0.25, value=6)
        freq = ui.select({1: "Annual", 2: "Semi-annual"}, value=2, label="Coupon frequency").classes("w-48")

        with ui.row().classes("w-full gap-8"):
            with ui.column().classes("gap-0"):
                ui.label("Bond price").classes("muted text-sm")
                price_out = ui.label().classes("stat-value")
            with ui.column().classes("gap-0"):
                ui.label("Trading at").classes("muted text-sm")
                status_out = ui.label().classes("stat-value")

        chart = ui.plotly(build_price_yield_figure(1000, 0.06, 10, 2, 0.06)).classes("w-full")

        def refresh() -> None:
            f, c, y, n, fr = face.value or 1, coupon.value / 100, ytm.value / 100, int(years.value), freq.value
            coupon_label.text = f"Coupon rate: {coupon.value}%"
            years_lbl.text = f"Years to maturity: {n}"
            yield_label.text = f"Market yield: {ytm.value}%"
            price = calc.bond_price(f, c, y, n, fr)
            price_out.text = inr(price)
            if abs(price - f) < 1:
                status_out.text, colour = "Par", TEAL
            elif price > f:
                status_out.text, colour = "Premium", TEAL
            else:
                status_out.text, colour = "Discount", AMBER
            status_out.style(f"color:{colour}")
            chart.update_figure(build_price_yield_figure(f, c, n, fr, y))

        for control in (face, coupon, years, ytm, freq):
            control.on_value_change(refresh)
        refresh()

        ui.label("Fintech connection").classes("text-2xl serif mt-4")
        ui.label(FINTECH_NOTE).classes("note")

        ui.label("Can you explain it?").classes("text-2xl serif mt-4")
        quiz(6, QUESTIONS)

        ui.link("Back to the learning path", "/").classes("mt-6")