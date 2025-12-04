"""Core compound interest calculations."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math


@dataclass
class YearlySnapshot:
    """Data for a single year in the projection."""

    year: int
    balance: Decimal
    interest_earned: Decimal
    contributions_ytd: Decimal
    ytd_growth_pct: float
    cumulative_interest: Decimal


@dataclass
class ProjectionResult:
    """Complete projection results."""

    principal: Decimal
    final_amount: Decimal
    total_interest: Decimal
    total_contributions: Decimal
    effective_apy: Decimal
    doubling_time: float
    rate: Decimal
    years: int
    compound_freq: int
    contribution: Decimal
    contribution_freq: int
    yearly_breakdown: list[YearlySnapshot]


def _round_currency(value: Decimal) -> Decimal:
    """Round to 2 decimal places for currency."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_effective_apy(rate: Decimal, compound_freq: int) -> Decimal:
    """Calculate effective annual percentage yield.

    APY = (1 + r/n)^n - 1
    """
    r = float(rate)
    n = compound_freq
    apy = (1 + r / n) ** n - 1
    return Decimal(str(apy))


def calculate_doubling_time(rate: Decimal, compound_freq: int) -> float:
    """Calculate time to double using the exact formula.

    t = ln(2) / (n * ln(1 + r/n))

    Falls back to Rule of 72 approximation if rate is very small.
    """
    r = float(rate)
    n = compound_freq

    if r <= 0:
        return float("inf")

    try:
        t = math.log(2) / (n * math.log(1 + r / n))
        return round(t, 1)
    except (ValueError, ZeroDivisionError):
        # Fallback to Rule of 72
        return round(72 / (r * 100), 1)


def calculate_compound_interest(
    principal: Decimal,
    rate: Decimal,
    years: int,
    compound_freq: int = 1,
    contribution: Decimal = Decimal("0"),
    contribution_freq: int = 12,
) -> ProjectionResult:
    """Calculate compound interest with optional regular contributions.

    Args:
        principal: Starting amount
        rate: Annual interest rate as decimal (0.07 for 7%)
        years: Number of years
        compound_freq: Compounding periods per year (1 = annually)
        contribution: Regular contribution amount
        contribution_freq: Contribution periods per year (12 = monthly)

    Returns:
        ProjectionResult with all calculated values
    """
    # Period rate for compounding
    period_rate = rate / compound_freq

    # Track balance and contributions
    balance = principal
    total_contributions = Decimal("0")
    cumulative_interest = Decimal("0")
    yearly_breakdown: list[YearlySnapshot] = []

    # Simulate year by year
    for year in range(1, years + 1):
        year_start_balance = balance
        year_interest = Decimal("0")
        year_contributions = Decimal("0")

        # Simulate each compounding period in the year
        for period in range(compound_freq):
            # Add interest for this period
            interest = balance * period_rate
            balance += interest
            year_interest += interest

            # Add contribution if this period aligns with contribution frequency
            # Simplified: spread contributions evenly across the year
            if contribution > 0:
                # Contribution happens at specific intervals
                periods_per_contribution = compound_freq // contribution_freq
                if periods_per_contribution == 0:
                    periods_per_contribution = 1

                if (period + 1) % periods_per_contribution == 0:
                    contrib_this_period = contribution
                    balance += contrib_this_period
                    year_contributions += contrib_this_period
                    total_contributions += contrib_this_period

        cumulative_interest += year_interest

        # Calculate YTD growth percentage
        if year_start_balance > 0:
            ytd_growth = float(year_interest / year_start_balance) * 100
        else:
            ytd_growth = 0.0

        yearly_breakdown.append(
            YearlySnapshot(
                year=year,
                balance=_round_currency(balance),
                interest_earned=_round_currency(year_interest),
                contributions_ytd=_round_currency(year_contributions),
                ytd_growth_pct=round(ytd_growth, 2),
                cumulative_interest=_round_currency(cumulative_interest),
            )
        )

    # Calculate summary metrics
    final_amount = _round_currency(balance)
    total_interest = _round_currency(cumulative_interest)
    effective_apy = calculate_effective_apy(rate, compound_freq)
    doubling_time = calculate_doubling_time(rate, compound_freq)

    return ProjectionResult(
        principal=principal,
        final_amount=final_amount,
        total_interest=total_interest,
        total_contributions=_round_currency(total_contributions),
        effective_apy=effective_apy,
        doubling_time=doubling_time,
        rate=rate,
        years=years,
        compound_freq=compound_freq,
        contribution=contribution,
        contribution_freq=contribution_freq,
        yearly_breakdown=yearly_breakdown,
    )
