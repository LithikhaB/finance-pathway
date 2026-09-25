"""Smoke tests for the UI layer using NiceGUI's built-in user simulation."""
import pytest
from nicegui import ui
from nicegui.testing import User

from app.pages.modules.module1 import build_figure, growth_series

pytest_plugins = ["nicegui.testing.user_plugin"]


def test_growth_series_matches_core():
    xs, nominal, real = growth_series(10_000, 0.10, 2, 1, 0.0)
    assert xs == [0, 1, 2]
    assert nominal[-1] == pytest.approx(12_100)
    assert real == pytest.approx(nominal)  # zero inflation: no adjustment


def test_figure_has_three_series():
    assert len(build_figure(1000, 0.08, 10, 12, 0.05).data) == 3


async def test_home_lists_modules(user: User):
    await user.open("/")
    await user.should_see("Time value of money")
    await user.should_see("Fintech business models")


async def test_module_1_renders_results(user: User):
    await user.open("/module/1")
    await user.should_see("Effective annual rate")
    await user.should_see("₹")


async def test_module_1_quiz_requires_answers(user: User):
    await user.open("/module/1")
    user.find(ui.button, content="Check answers").click()
    await user.should_see("Answer every question first.")


async def test_module_5_renders_results(user: User):
    await user.open("/module/5")
    await user.should_see("Monthly EMI")
    await user.should_see("₹")


async def test_module_5_emi_matches_core():
    from core.calculations import emi
    assert emi(500_000, 0.09, 60) == pytest.approx(10379.18, abs=0.01)


async def test_calculator_appears_on_module_page(user: User):
    await user.open("/module/1")
    await user.should_see("Calculator")


async def test_calculator_adds(user: User):
    await user.open("/module/1")
    user.find(ui.button, content="7").click()
    user.find(ui.button, content="+").click()
    user.find(ui.button, content="3").click()
    user.find(ui.button, content="=").click()
    await user.should_see("10")


def test_progress_resets():
    from app.services import progress
    progress.record_score(99, 3, 3)
    assert progress.get(99) is not None
    progress.reset()
    assert progress.get(99) is None


async def test_module_2_renders_and_computes(user: User):
    await user.open("/module/2")
    await user.should_see("NPV at this rate")
    await user.should_see("IRR")


async def test_module_2_npv_matches_core():
    from core.calculations import npv
    assert npv(0.10, [-100, 110]) == pytest.approx(0)


async def test_module_3_ledger_posts_and_balances(user: User):
    await user.open("/module/3")
    await user.should_see("books balance")
    user.find(ui.button, content="Customer deposits \u20b910,000").click()
    await user.should_see("\u20b910,000")  # the posted transaction's amount appears in the ledger


async def test_module_4_trace_a_payment(user: User):
    await user.open("/module/4")
    await user.should_see("Authorization")
    await user.should_see("Settlement")


async def test_module_6_bond_price_renders(user: User):
    await user.open("/module/6")
    await user.should_see("Bond price")
    await user.should_see("Trading at")


def test_module_6_bond_price_matches_core():
    from core.calculations import bond_price
    assert bond_price(1000, 0.06, 0.06, 10) == pytest.approx(1000)


async def test_module_7_sip_renders(user: User):
    await user.open("/module/7")
    await user.should_see("Portfolio value")
    await user.should_see("Growth from returns")


def test_module_7_sip_matches_core():
    from core.calculations import sip_future_value
    assert sip_future_value(5000, 0.12, 12) == pytest.approx(64046.64, abs=0.01)


async def test_module_8_var_renders(user: User):
    await user.open("/module/8")
    await user.should_see("Value at Risk")
    await user.should_see("Operational risk")


def test_module_8_var_matches_core():
    from core.calculations import value_at_risk
    assert value_at_risk(1_000_000, 0.02, 0.95, 1) == pytest.approx(32898, abs=1)


async def test_module_9_kyc_flow_switches(user: User):
    await user.open("/module/9")
    await user.should_see("Identity verification")
    user.find(ui.select).click()
    user.find("Business").click()
    await user.should_see("Beneficial ownership")


async def test_module_10_unit_economics_renders(user: User):
    await user.open("/module/10")
    await user.should_see("LTV : CAC")
    await user.should_see("Payback period")


def test_module_10_ratio_matches_core():
    from core.calculations import ltv_cac_ratio
    assert ltv_cac_ratio(500, 0.6, 0.05, 1500) == pytest.approx(4.0)