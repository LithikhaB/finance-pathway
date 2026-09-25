"""Pure finance formulas. No UI code, no I/O.

Conventions
-----------
* Rates are decimals: 10% -> 0.10
* Annual rates are nominal unless the function says "effective".
* Cash flow lists start at t=0 (usually an outflow, so negative).
"""
from __future__ import annotations


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------- Module 1
def compound_interest(
    principal: float, annual_rate: float, years: float, compounds_per_year: int = 1
) -> float:
    """Future value: P * (1 + r/n) ** (n * t)."""
    _require(principal >= 0, "principal must be non-negative")
    _require(years >= 0, "years must be non-negative")
    _require(compounds_per_year >= 1, "compounds_per_year must be >= 1")
    n = compounds_per_year
    return principal * (1 + annual_rate / n) ** (n * years)


def effective_annual_rate(nominal_rate: float, compounds_per_year: int) -> float:
    """EAR = (1 + r/n) ** n - 1."""
    _require(compounds_per_year >= 1, "compounds_per_year must be >= 1")
    return (1 + nominal_rate / compounds_per_year) ** compounds_per_year - 1


def real_rate(nominal_rate: float, inflation: float) -> float:
    """Fisher equation: (1 + nominal) / (1 + inflation) - 1."""
    _require(inflation > -1, "inflation must be greater than -100%")
    return (1 + nominal_rate) / (1 + inflation) - 1


def present_value(future_value: float, annual_rate: float, years: float) -> float:
    """Discount a future amount back to today."""
    _require(annual_rate > -1, "rate must be greater than -100%")
    return future_value / (1 + annual_rate) ** years


# ---------------------------------------------------------------- Module 2
def cagr(begin_value: float, end_value: float, years: float) -> float:
    """Compound annual growth rate."""
    _require(begin_value > 0 and end_value > 0, "values must be positive")
    _require(years > 0, "years must be positive")
    return (end_value / begin_value) ** (1 / years) - 1


def npv(rate: float, cash_flows: list[float]) -> float:
    """Net present value. cash_flows[0] occurs at t=0."""
    _require(rate > -1, "rate must be greater than -100%")
    _require(len(cash_flows) > 0, "cash_flows cannot be empty")
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))


def irr(cash_flows: list[float], low: float = -0.99, high: float = 10.0,
        tol: float = 1e-10, max_iter: int = 500) -> float:
    """Internal rate of return via bisection.

    Needs at least one negative and one positive cash flow.
    """
    _require(
        any(cf < 0 for cf in cash_flows) and any(cf > 0 for cf in cash_flows),
        "cash flows need at least one negative and one positive value",
    )
    f_low, f_high = npv(low, cash_flows), npv(high, cash_flows)
    _require(f_low * f_high < 0, "no sign change in range; IRR not bracketed")
    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = npv(mid, cash_flows)
        if abs(f_mid) < tol or (high - low) / 2 < tol:
            return mid
        if f_low * f_mid < 0:
            high = mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


# ---------------------------------------------------------------- Module 5
def emi(principal: float, annual_rate: float, months: int) -> float:
    """Equated monthly instalment: P*r*(1+r)^n / ((1+r)^n - 1)."""
    _require(principal > 0, "principal must be positive")
    _require(months >= 1, "months must be >= 1")
    _require(annual_rate >= 0, "rate must be non-negative")
    r = annual_rate / 12
    if r == 0:
        return principal / months
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def amortization_schedule(principal: float, annual_rate: float, months: int) -> list[dict]:
    """Month-by-month split of each EMI into interest and principal."""
    payment = emi(principal, annual_rate, months)
    r = annual_rate / 12
    balance = principal
    rows = []
    for month in range(1, months + 1):
        interest = balance * r
        principal_paid = payment - interest
        if month == months:  # clear tiny floating point residue
            principal_paid = balance
            payment_this_month = principal_paid + interest
        else:
            payment_this_month = payment
        balance -= principal_paid
        rows.append({
            "month": month,
            "payment": payment_this_month,
            "interest": interest,
            "principal": principal_paid,
            "balance": max(balance, 0.0),
        })
    return rows


# ---------------------------------------------------------------- Module 6
def bond_price(face_value: float, coupon_rate: float, ytm: float,
               years: int, payments_per_year: int = 2) -> float:
    """Price of a plain-vanilla coupon bond as the PV of its cash flows."""
    _require(years > 0 and payments_per_year >= 1, "invalid maturity or frequency")
    n = years * payments_per_year
    coupon = face_value * coupon_rate / payments_per_year
    y = ytm / payments_per_year
    _require(y > -1, "yield must be greater than -100%")
    pv_coupons = sum(coupon / (1 + y) ** t for t in range(1, n + 1))
    pv_face = face_value / (1 + y) ** n
    return pv_coupons + pv_face


# ---------------------------------------------------------------- Module 7
def sip_future_value(monthly_amount: float, annual_rate: float, months: int,
                     payment_at_start: bool = True) -> float:
    """Future value of a monthly SIP (systematic investment plan).

    Assumes the annual rate is split evenly into monthly rates.
    payment_at_start=True matches most Indian SIP calculators.
    """
    _require(monthly_amount >= 0 and months >= 0, "invalid SIP inputs")
    i = annual_rate / 12
    if i == 0:
        return monthly_amount * months
    fv = monthly_amount * (((1 + i) ** months - 1) / i)
    return fv * (1 + i) if payment_at_start else fv


# ---------------------------------------------------------------- Module 10
def ltv_cac_ratio(avg_revenue_per_month: float, gross_margin: float,
                  monthly_churn: float, cac: float) -> float:
    """Customer lifetime value divided by acquisition cost.

    LTV = monthly revenue * gross margin / monthly churn. A common rule of
    thumb is that a ratio above 3 is healthy.
    """
    _require(monthly_churn > 0, "churn must be positive")
    _require(cac > 0, "CAC must be positive")
    ltv = avg_revenue_per_month * gross_margin / monthly_churn
    return ltv / cac


def cac_payback_months(avg_revenue_per_month: float, gross_margin: float, cac: float) -> float:
    """Months of gross-margin revenue needed to recover the cost of acquiring a customer."""
    _require(avg_revenue_per_month > 0, "revenue must be positive")
    _require(gross_margin > 0, "gross margin must be positive")
    _require(cac > 0, "CAC must be positive")
    return cac / (avg_revenue_per_month * gross_margin)


# ---------------------------------------------------------------- Module 8
def value_at_risk(portfolio_value: float, daily_volatility: float,
                  confidence: float = 0.95, days: int = 1) -> float:
    """Parametric (variance-covariance) VaR, assuming normally distributed returns.

    Returns the loss magnitude expected NOT to be exceeded with the given
    confidence over the given horizon. E.g. a 95% 1-day VaR of 10,000 means
    a loss beyond 10,000 in a single day is expected only 5% of the time.
    """
    import math
    z_scores = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}
    _require(confidence in z_scores, "confidence must be 0.90, 0.95, or 0.99")
    _require(portfolio_value >= 0 and daily_volatility >= 0, "value and volatility must be non-negative")
    _require(days >= 1, "days must be >= 1")
    return portfolio_value * daily_volatility * z_scores[confidence] * math.sqrt(days)