"""Render a formula the way a textbook would: stacked fractions, italic
variables, superscripts, not a single flat line of code.

Usage
-----
formula(
    "FV = P (1 + " + frac("r", "n") + ")" + sup("n" + times() + "t"),
    key="P principal, r yearly rate, n times compounded per year, t years",
)
"""
from nicegui import ui


def var(name: str) -> str:
    return f'<span class="var">{name}</span>'


def frac(numerator: str, denominator: str) -> str:
    return (
        '<span class="frac">'
        f'<span class="num">{numerator}</span>'
        f'<span class="den">{denominator}</span>'
        "</span>"
    )


def sup(text: str) -> str:
    return f"<sup>{text}</sup>"


def sub(text: str) -> str:
    return f"<sub>{text}</sub>"


def times() -> str:
    return " \u00d7 "  # ×


def formula(expression: str, key: str | None = None) -> None:
    """Display one formula, optionally followed by a small legend of its symbols."""
    html = f'<div class="formula">{expression}'
    if key:
        html += f'<div class="key">{key}</div>'
    html += "</div>"
    ui.html(html)