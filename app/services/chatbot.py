"""Two features share this module: the sidebar chatbot and the company
lookup page.

If a GROQ_API_KEY environment variable is set (and the `groq` package is
installed), both are answered by a Groq-hosted model. Without a key, each
falls back to a small built-in dictionary, so the app is fully usable with
no external service configured, and gives a clear message when a topic or
company isn't covered.
"""
import os

_MODEL = "openai/gpt-oss-20b"

_CHAT_SYSTEM_PROMPT = (
    "You are a friendly finance tutor inside a personal-finance and fintech "
    "learning app called Finance Pathway. Answer in 3 to 5 plain-language "
    "sentences, and relate the answer back to fintech where it fits. You are "
    "not a licensed financial advisor, so add a brief reminder to that effect "
    "only if the question asks for personal investment, tax, or legal advice."
)

_CHAT_FAQ = {
    "compound interest": "Compound interest is interest earned on your earlier interest, not just your original amount, so money left to grow for longer accelerates. See Module 1 for the formula and a calculator.",
    "effective annual rate": "The effective annual rate (EAR) is what a rate actually earns or costs in a year once compounding is counted, which is why a '12% monthly' rate really works out to about 12.68%. See Module 1.",
    "emi": "EMI (equated monthly instalment) is the fixed monthly payment that clears a loan, made up of shrinking interest and growing principal each month. See Module 5.",
    "npv": "NPV (net present value) sums a project's future cash flows, each discounted back to today's value. A positive NPV means the investment is expected to be worth more than it costs. See Module 2.",
    "irr": "IRR (internal rate of return) is the discount rate that makes a project's NPV exactly zero, essentially its own break-even return. See Module 2.",
    "double-entry": "Double-entry bookkeeping records every transaction as an equal debit and credit, so a bank's books always balance: assets equal liabilities plus equity. See Module 3.",
    "kyc": "KYC (Know Your Customer) is the process of verifying who a customer is, usually with a government ID and address proof, before letting them transact. See Module 9.",
    "bond": "A bond is a loan: the issuer promises fixed coupon payments and the face value back at maturity. Bond prices and yields move in opposite directions. See Module 6.",
    "diversification": "Diversification spreads money across many investments so one bad outcome doesn't sink the whole portfolio. It reduces risk, not raise expected return. See Module 7.",
    "var": "Value at Risk (VaR) estimates the loss a portfolio is not expected to exceed, at a given confidence level, over a given time period. See Module 8.",
    "ltv": "LTV (customer lifetime value) estimates the total profit a customer generates over time. Compared against CAC, the cost to acquire them, it shows whether a business model works. See Module 10.",
    "cac": "CAC is the cost of acquiring one customer. A healthy business usually wants its LTV:CAC ratio above 3, and a payback period under about 12 months. See Module 10.",
}


def _fallback(question: str, faq: dict[str, str], topic_word: str) -> str:
    q = question.lower()
    for keyword, answer in faq.items():
        if keyword in q:
            return answer
    examples = ", ".join(list(faq)[:6])
    return (
        f"I don't have a built-in answer for that {topic_word} yet. Try asking about "
        f"one of: {examples}, or set a GROQ_API_KEY environment variable to "
        "enable open-ended answers."
    )


def _call_groq(system: str, user_message: str, max_tokens: int = 400) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
    except ImportError:
        return "(chatbot service unavailable: the 'groq' package isn't installed \u2014 run `pip install groq`)"
    try:
        client = Groq(api_key=api_key)
        model = os.environ.get("GROQ_MODEL", _MODEL)
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
    except Exception as exc:  # network issues, bad key, rate limit, etc.
        return f"(chatbot service unavailable: {exc.__class__.__name__})"


def ask(question: str) -> str:
    """Answer a free-form finance question for the sidebar chatbot."""
    answer = _call_groq(_CHAT_SYSTEM_PROMPT, question)
    if answer is None:
        return _fallback(question, _CHAT_FAQ, "term")
    if answer.startswith("(chatbot service unavailable"):
        return f"{answer}. Here's a quick answer instead:\n\n{_fallback(question, _CHAT_FAQ, 'term')}"
    return answer


_COMPANY_SYSTEM_PROMPT = (
    "You explain what a company does for a student studying fintech. In "
    "under 150 words, cover: what the company does, its core revenue model, "
    "and how it moves or manages money (payments, lending, deposits, or "
    "similar). Be factual and neutral, and note if you are unsure of recent "
    "details."
)

_COMPANY_FAQ = {
    "citigroup": "Citigroup (Citi) is a global bank offering consumer banking, credit cards, and institutional services like corporate lending, trading, and treasury and cash management. It earns through net interest margin on loans and deposits, card interchange and fees, and fees for institutional services. As a systemically important bank, Citi moves money at huge scale across currencies and borders, and is closely supervised by regulators such as the US Federal Reserve and OCC.",
    "citi": "Citigroup (Citi) is a global bank offering consumer banking, credit cards, and institutional services like corporate lending, trading, and treasury and cash management. It earns through net interest margin on loans and deposits, card interchange and fees, and fees for institutional services. As a systemically important bank, Citi moves money at huge scale across currencies and borders, and is closely supervised by regulators such as the US Federal Reserve and OCC.",
    "jpmorgan chase": "JPMorgan Chase is one of the largest global banks, spanning consumer banking, credit cards, investment banking, and asset management. It earns through net interest margin, trading and advisory fees, and card fees. It moves enormous volumes of money daily, including clearing and settling payments for other banks and institutions worldwide.",
    "paypal": "PayPal is a digital payments company that lets people and businesses send and receive money online. It earns mainly through transaction fees, a percentage of each payment processed, plus fees on services like currency conversion and instant transfers. PayPal holds customer balances and settles transactions between buyers, sellers, and banks, acting as a payment intermediary rather than a bank in most countries.",
    "stripe": "Stripe is a payments infrastructure company that lets other businesses accept online payments. Its core revenue model is a take rate: a small percentage plus a fixed fee on every transaction it processes. Stripe handles the technical and compliance complexity of moving money between a customer's card or bank and a merchant's account, including fraud checks and settlement.",
    "paytm": "Paytm is an Indian fintech offering a mobile wallet, UPI payments, and financial services like lending and insurance distribution. It earns through payment processing fees, commissions on financial products it distributes, and advertising on its app. It moves money by holding customer wallet balances and routing UPI transactions between banks in real time.",
    "razorpay": "Razorpay is an Indian payments and banking infrastructure company that helps businesses accept and disburse payments. It earns a take rate on transactions processed, plus fees for additional services like payroll and lending. It sits between merchants and banks or card networks, handling authorization, routing, and settlement of funds.",
    "square": "Square, part of Block, provides payment processing and point-of-sale hardware and software mainly for small businesses, alongside the Cash App consumer payments product. It earns a take rate on transactions and fees for services like instant deposits and loans, moving money between customers, merchants, and their banks.",
    "block": "Block (formerly Square) provides payment processing and point-of-sale tools for small businesses, plus the consumer Cash App. It earns a take rate on transactions and fees for services like instant deposits, loans, and Bitcoin trading, moving money between customers, merchants, and their banks.",
    "robinhood": "Robinhood is a US brokerage app offering commission-free stock, options, and crypto trading. It earns mainly through payment for order flow, interest on uninvested cash and margin lending, and subscription fees. It moves customer money into and out of markets, typically settling trades one business day after the trade (T+1).",
}


def explain_company(name: str) -> str:
    """Return a short explanation of what a company does and how it handles money."""
    key = name.strip().lower()
    if not key:
        return "Enter a company name to look up."
    answer = _call_groq(_COMPANY_SYSTEM_PROMPT, f"Explain the company: {name}")
    if answer is not None and not answer.startswith("(chatbot service unavailable"):
        return answer
    if key in _COMPANY_FAQ:
        return _COMPANY_FAQ[key]
    examples = ", ".join(sorted({n.title() for n in _COMPANY_FAQ}))
    return (
        f"I don't have a built-in profile for '{name}' yet. Try one of: {examples}, "
        "or set a GROQ_API_KEY environment variable for open-ended lookups."
    )