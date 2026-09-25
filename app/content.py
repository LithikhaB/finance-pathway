"""Curriculum registry. `live=True` modules have a page; others show as coming soon."""

STAGES = [
    {
        "name": "Stage 1: Money fundamentals",
        "tagline": "The language every other module builds on.",
        "modules": [
            {"id": 1, "title": "Time value of money",
             "summary": "Compounding, effective rate, inflation and real returns.", "live": True},
            {"id": 2, "title": "Cash flows and valuation",
             "summary": "NPV, IRR, CAGR and discounting.", "live": True},
        ],
    },
    {
        "name": "Stage 2: How the financial system works",
        "tagline": "The plumbing behind every fintech product.",
        "modules": [
            {"id": 3, "title": "Banking and ledgers",
             "summary": "Accounts, double-entry bookkeeping, reconciliation.", "live": True},
            {"id": 4, "title": "Payments",
             "summary": "Cards, UPI, ACH, SWIFT; authorization, clearing, settlement.", "live": True},
            {"id": 5, "title": "Lending and credit",
             "summary": "EMI, APR, amortization, credit scores, underwriting.", "live": True},
        ],
    },
    {
        "name": "Stage 3: Markets and risk",
        "tagline": "How money is priced and how losses are contained.",
        "modules": [
            {"id": 6, "title": "Capital markets",
             "summary": "Equities, bonds, derivatives basics, order lifecycle, settlement.", "live": True},
            {"id": 7, "title": "Investing and portfolios",
             "summary": "Risk vs return, diversification, SIP, asset allocation.", "live": True},
            {"id": 8, "title": "Risk management",
             "summary": "Credit, market, liquidity, operational and fraud risk.", "live": True},
        ],
    },
    {
        "name": "Stage 4: Rules and business",
        "tagline": "What regulators require and how fintechs make money.",
        "modules": [
            {"id": 9, "title": "Regulation and compliance",
             "summary": "KYC, AML, PCI-DSS, data privacy, RBI and global regulators.", "live": True},
            {"id": 10, "title": "Fintech business models",
             "summary": "Take rate, NIM, CAC, LTV, unit economics, BNPL.", "live": True},
        ],
    },
]


def all_modules() -> list[dict]:
    return [m for s in STAGES for m in s["modules"]]


def live_modules() -> list[dict]:
    return [m for m in all_modules() if m["live"]]