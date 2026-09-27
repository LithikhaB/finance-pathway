"""Smoke tests for the UI layer using NiceGUI's built-in user simulation."""
import pytest
from nicegui import ui
from nicegui.testing import User

from app.pages.modules.module1 import build_figure, growth_series

pytest_plugins = ["nicegui.testing.user_plugin"]

_counter = {"n": 0}


async def _login(user: User) -> str:
    """Sign up a fresh, unique test user and land back on the home page."""
    _counter["n"] += 1
    username = f"tester{_counter['n']}"
    await user.open("/login")
    user.find(marker="login-username").type(username)
    user.find(marker="login-password").type("password123")
    user.find(kind=ui.button, content="New here? Create an account").click()
    await user.should_see("Create an account")
    user.find(kind=ui.button, content="Sign up").click()
    await user.should_see("Time value of money")
    return username


def test_growth_series_matches_core():
    xs, nominal, real = growth_series(10_000, 0.10, 2, 1, 0.0)
    assert xs == [0, 1, 2]
    assert nominal[-1] == pytest.approx(12_100)
    assert real == pytest.approx(nominal)  # zero inflation: no adjustment


def test_figure_has_three_series():
    assert len(build_figure(1000, 0.08, 10, 12, 0.05).data) == 3


async def test_root_redirects_to_login_when_signed_out(user: User):
    await user.open("/")
    await user.should_see("Log in")


async def test_home_lists_modules(user: User):
    await _login(user)
    await user.should_see("Time value of money")
    await user.should_see("Fintech business models")


async def test_module_1_renders_results(user: User):
    await _login(user)
    await user.open("/module/1")
    await user.should_see("Effective annual rate")
    await user.should_see("₹")


async def test_module_1_quiz_requires_answers(user: User):
    await _login(user)
    await user.open("/module/1")
    user.find(kind=ui.button, content="Check answers").click()
    await user.should_see("Answer every question first.")


async def test_module_5_renders_results(user: User):
    await _login(user)
    await user.open("/module/5")
    await user.should_see("Monthly EMI")
    await user.should_see("₹")


async def test_module_5_emi_matches_core():
    from core.calculations import emi
    assert emi(500_000, 0.09, 60) == pytest.approx(10379.18, abs=0.01)


async def test_calculator_appears_on_module_page(user: User):
    await _login(user)
    await user.open("/module/1")
    await user.should_see("Calculator")


async def test_calculator_adds(user: User):
    await _login(user)
    await user.open("/module/1")
    user.find(kind=ui.button, content="7").click()
    user.find(kind=ui.button, content="+").click()
    user.find(kind=ui.button, content="3").click()
    user.find(kind=ui.button, content="=").click()
    await user.should_see("10")


async def test_progress_resets(user: User):
    await _login(user)  # gives the in-memory progress store an active user context
    from app.services import progress
    progress.record_score(99, 3, 3)
    assert progress.get(99) is not None
    progress.reset()
    assert progress.get(99) is None


async def test_module_2_renders_and_computes(user: User):
    await _login(user)
    await user.open("/module/2")
    await user.should_see("NPV at this rate")
    await user.should_see("IRR")


async def test_module_2_npv_matches_core():
    from core.calculations import npv
    assert npv(0.10, [-100, 110]) == pytest.approx(0)


async def test_module_3_ledger_posts_and_balances(user: User):
    await _login(user)
    await user.open("/module/3")
    await user.should_see("books balance")
    user.find(kind=ui.button, content="Customer deposits \u20b910,000").click()
    await user.should_see("\u20b910,000")  # the posted transaction's amount appears in the ledger


async def test_module_4_trace_a_payment(user: User):
    await _login(user)
    await user.open("/module/4")
    await user.should_see("Authorization")
    await user.should_see("Settlement")


async def test_module_6_bond_price_renders(user: User):
    await _login(user)
    await user.open("/module/6")
    await user.should_see("Bond price")
    await user.should_see("Trading at")


def test_module_6_bond_price_matches_core():
    from core.calculations import bond_price
    assert bond_price(1000, 0.06, 0.06, 10) == pytest.approx(1000)


async def test_module_7_sip_renders(user: User):
    await _login(user)
    await user.open("/module/7")
    await user.should_see("Portfolio value")
    await user.should_see("Growth from returns")


def test_module_7_sip_matches_core():
    from core.calculations import sip_future_value
    assert sip_future_value(5000, 0.12, 12) == pytest.approx(64046.64, abs=0.01)


async def test_module_8_var_renders(user: User):
    await _login(user)
    await user.open("/module/8")
    await user.should_see("Value at Risk")
    await user.should_see("Operational risk")


def test_module_8_var_matches_core():
    from core.calculations import value_at_risk
    assert value_at_risk(1_000_000, 0.02, 0.95, 1) == pytest.approx(32898, abs=1)


async def test_module_9_kyc_flow_switches(user: User):
    await _login(user)
    await user.open("/module/9")
    await user.should_see("Identity verification")
    user.find(ui.select).click()
    user.find("Business").click()
    await user.should_see("Beneficial ownership")


async def test_module_10_unit_economics_renders(user: User):
    await _login(user)
    await user.open("/module/10")
    await user.should_see("LTV : CAC")
    await user.should_see("Payback period")


def test_module_10_ratio_matches_core():
    from core.calculations import ltv_cac_ratio
    assert ltv_cac_ratio(500, 0.6, 0.05, 1500) == pytest.approx(4.0)


async def test_signup_then_login_roundtrip(user: User):
    username = await _login(user)
    await user.should_see("Time value of money")
    # log out, then log back in with the same credentials
    user.find(marker="logout-button").click()
    await user.should_see("Log in")
    user.find(marker="login-username").type(username)
    user.find(marker="login-password").type("password123")
    user.find(kind=ui.button, content="Log in").click()
    await user.should_see("Time value of money")


async def test_wrong_password_rejected(user: User):
    username = await _login(user)
    user.find(marker="logout-button").click()
    await user.should_see("Log in")
    user.find(marker="login-username").type(username)
    user.find(marker="login-password").type("not-the-password")
    user.find(kind=ui.button, content="Log in").click()
    await user.should_see("Incorrect username or password.")


def test_password_is_hashed_not_stored_plain():
    from app.services import auth
    from app.services.db import connect
    ok, _ = auth.register("hash-check-user", "supersecret")
    assert ok
    with connect() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", ("hash-check-user",)
        ).fetchone()
    assert row["password_hash"] != "supersecret"
    assert auth.verify("hash-check-user", "supersecret")
    assert not auth.verify("hash-check-user", "wrong")


async def test_progress_persists_across_a_fresh_db_connection(user: User):
    await _login(user)
    from app.services import progress
    progress.record_score(1, 3, 3)
    entry = progress.get(1)
    assert entry is not None
    assert entry["done"] is True
    # a brand new connection (simulating a restart reading the same file) sees it too
    from app.services.db import connect
    with connect() as conn:
        row = conn.execute(
            "SELECT score, done FROM progress WHERE module_id = 1"
        ).fetchone()
    assert row["score"] == 3
    assert row["done"] == 1


def test_chatbot_fallback_answers_known_term():
    from app.services import chatbot
    answer = chatbot.ask("What is compound interest?")
    assert "compound" in answer.lower() or "interest" in answer.lower()


def test_strip_markdown_removes_bold_and_bullets():
    from app.services.chatbot import _strip_markdown
    raw = "**NPV** is useful.\n- First point\n- Second point\n# A header\n*italic* text"
    cleaned = _strip_markdown(raw)
    assert "*" not in cleaned
    assert "#" not in cleaned
    assert "NPV" in cleaned
    assert "First point" in cleaned


def test_chatbot_fallback_unknown_term_points_to_examples():
    from app.services import chatbot
    answer = chatbot.ask("What is quantum computing?")
    assert "don't have a built-in answer" in answer


def test_company_lookup_known_company():
    from app.services import chatbot
    answer = chatbot.explain_company("Citigroup")
    assert "citi" in answer.lower()
    assert "\n\n" in answer  # two paragraphs


def test_company_lookup_unknown_company_lists_examples():
    from app.services import chatbot
    answer = chatbot.explain_company("Some Made Up Fintech Inc")
    assert "don't have a built-in profile" in answer


async def test_company_page_renders_and_looks_up(user: User):
    await _login(user)
    await user.open("/company")
    await user.should_see("Company lookup")
    user.find(marker="company-name-input").type("Citigroup")
    user.find(marker="company-lookup-button").click()
    await user.should_see("Citigroup")


async def test_home_links_to_company_lookup(user: User):
    await _login(user)
    await user.should_see("Company lookup")


async def test_chat_widget_opens_and_answers(user: User):
    await _login(user)
    await user.open("/module/1")
    user.find(marker="chat-bubble").click()
    await user.should_see("Ask about finance")
    await user.should_see("Ask me about any term from the curriculum")
    user.find(marker="chat-question-input").type("What is compound interest?")
    user.find(marker="chat-send-button").click()
    await user.should_see("What is compound interest?")
    await user.should_see("compound interest")


async def test_chat_close_button_actually_closes(user: User):
    await _login(user)
    await user.open("/module/1")
    bubble = user.find(marker="chat-bubble")
    bubble.click()
    await user.should_see("Ask about finance")
    user.find(marker="chat-close-button").click()
    # bubble should regain its visible (non-hidden) class once closed
    bubble_el = next(iter(user.find(marker="chat-bubble").elements))
    assert "chat-bubble-hidden" not in bubble_el._classes