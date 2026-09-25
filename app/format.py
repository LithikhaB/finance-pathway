def inr(amount: float) -> str:
    """Format a number as rupees with Indian digit grouping (12,34,567)."""
    sign = "-" if amount < 0 else ""
    digits = f"{abs(amount):.0f}"
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ",".join(groups + [tail])
    return f"{sign}₹{digits}"


def pct(x: float, places: int = 2) -> str:
    return f"{x * 100:.{places}f}%"