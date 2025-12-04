"""Utility functions for parsing and formatting."""

from decimal import Decimal
import re

FREQUENCY_MAP = {
    "daily": 365,
    "weekly": 52,
    "biweekly": 26,
    "monthly": 12,
    "quarterly": 4,
    "semiannually": 2,
    "annually": 1,
    "yearly": 1,
}


def parse_rate(value: str | float | Decimal) -> Decimal:
    """Parse a rate from various formats.

    Accepts:
        - "7%" or "7 %" -> 0.07
        - "0.07" -> 0.07
        - ".07" -> 0.07
        - 7 (int/float, assumed percent if >= 1) -> 0.07
        - 0.07 (float) -> 0.07
    """
    if isinstance(value, Decimal):
        return value if value < 1 else value / 100

    if isinstance(value, (int, float)):
        return Decimal(str(value)) if value < 1 else Decimal(str(value)) / 100

    # String handling
    value = str(value).strip()

    # Check for percentage sign
    if "%" in value:
        num = Decimal(re.sub(r"[%\s]", "", value))
        return num / 100

    # Plain number
    num = Decimal(value)
    # Assume values >= 1 are percentages (e.g., 7 means 7%)
    return num if num < 1 else num / 100


def parse_frequency(value: str | int) -> int:
    """Parse compounding frequency from string or int.

    Accepts:
        - "monthly", "daily", etc. (case-insensitive)
        - Integer directly (12, 365, etc.)
    """
    if isinstance(value, int):
        return value

    value = str(value).strip().lower()

    if value in FREQUENCY_MAP:
        return FREQUENCY_MAP[value]

    # Try parsing as integer
    try:
        return int(value)
    except ValueError:
        valid = ", ".join(FREQUENCY_MAP.keys())
        raise ValueError(f"Invalid frequency '{value}'. Use: {valid} or an integer.")


def format_currency(amount: Decimal | float, symbol: str = "$") -> str:
    """Format a number as currency with commas and 2 decimal places."""
    return f"{symbol}{float(amount):,.2f}"


def format_percent(rate: Decimal | float, decimals: int = 2) -> str:
    """Format a decimal rate as a percentage string."""
    return f"{float(rate) * 100:.{decimals}f}%"
