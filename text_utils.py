"""Shared text-formatting helpers for user-facing output.

Centralizes grammar so no engine ever emits '2th house' again.
"""


def ordinal(n: int) -> str:
    """Return the English ordinal string for an integer (1 -> '1st', 2 -> '2nd', 11 -> '11th')."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
