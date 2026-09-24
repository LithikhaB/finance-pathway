import pytest

from core import calculations as c


# ------------------------------------------------------------ time value
def test_compound_interest_known_value():
    assert c.compound_interest(10_000, 0.10, 2) == pytest.approx(12_100)


def test_compound_interest_monthly_beats_annual():
    assert c.compound_interest(1000, 0.12, 1, 12) > c.compound_interest(1000, 0.12, 1, 1)


def test_effective_annual_rate_monthly_12pct():
    assert c.effective_annual_rate(0.12, 12) == pytest.approx(0.126825, abs=1e-6)


def test_real_rate():
    assert c.real_rate(0.10, 0.05) == pytest.approx(0.047619, abs=1e-6)


def test_present_value_round_trip():
    fv = c.compound_interest(5000, 0.08, 5)
    assert c.present_value(fv, 0.08, 5) == pytest.approx(5000)


def test_negative_principal_rejected():
    with pytest.raises(ValueError):
        c.compound_interest(-1, 0.05, 1)


# ------------------------------------------------------------ valuation
def test_cagr():
    assert c.cagr(100, 121, 2) == pytest.approx(0.10)


def test_npv_zero_at_irr():
    assert c.npv(0.10, [-100, 110]) == pytest.approx(0)


def test_irr_simple():
    assert c.irr([-100, 110]) == pytest.approx(0.10, abs=1e-6)


def test_irr_multi_period_is_consistent_with_npv():
    flows = [-1000, 300, 400, 500]
    rate = c.irr(flows)
    assert c.npv(rate, flows) == pytest.approx(0, abs=1e-6)


def test_irr_needs_sign_change():
    with pytest.raises(ValueError):
        c.irr([100, 200, 300])


# ------------------------------------------------------------ loans
def test_emi_known_value():
    # 1,00,000 at 12% for 12 months -> 8,884.88 (standard textbook figure)
    assert c.emi(100_000, 0.12, 12) == pytest.approx(8884.88, abs=0.01)


def test_emi_zero_rate():
    assert c.emi(12_000, 0.0, 12) == pytest.approx(1000)


def test_amortization_clears_loan():
    rows = c.amortization_schedule(500_000, 0.09, 60)
    assert len(rows) == 60
    assert rows[-1]["balance"] == pytest.approx(0, abs=1e-6)
    assert sum(r["principal"] for r in rows) == pytest.approx(500_000)


def test_amortization_interest_falls_over_time():
    rows = c.amortization_schedule(500_000, 0.09, 60)
    assert rows[0]["interest"] > rows[-1]["interest"]


# ------------------------------------------------------------ bonds
def test_bond_at_par_when_coupon_equals_yield():
    assert c.bond_price(1000, 0.06, 0.06, 10) == pytest.approx(1000)


def test_bond_price_falls_when_yield_rises():
    assert c.bond_price(1000, 0.06, 0.08, 10) < 1000 < c.bond_price(1000, 0.06, 0.04, 10)


# ------------------------------------------------------------ SIP
def _simulate_sip(amount, annual_rate, months, at_start):
    i, balance = annual_rate / 12, 0.0
    for _ in range(months):
        if at_start:
            balance += amount
        balance *= 1 + i
        if not at_start:
            balance += amount
    return balance


@pytest.mark.parametrize("at_start", [True, False])
def test_sip_matches_month_by_month_simulation(at_start):
    expected = _simulate_sip(5000, 0.12, 120, at_start)
    assert c.sip_future_value(5000, 0.12, 120, at_start) == pytest.approx(expected)


def test_sip_zero_rate():
    assert c.sip_future_value(1000, 0.0, 24) == 24_000


# ------------------------------------------------------------ unit economics
def test_ltv_cac_ratio():
    # 20 revenue/month, 50% margin, 5% churn -> LTV 200; CAC 50 -> 4.0
    assert c.ltv_cac_ratio(20, 0.5, 0.05, 50) == pytest.approx(4.0)