"""JSON formatter for machine-readable output."""

import json
from decimal import Decimal

from compound.calculator import ProjectionResult
from compound.formatters import RenderOptions


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class JsonFormatter:
    """Formatter that outputs JSON."""

    def render(self, result: ProjectionResult, options: RenderOptions) -> str:
        """Render projection as JSON."""
        if options.quiet:
            return json.dumps({"final_amount": float(result.final_amount)})

        data = {
            "summary": {
                "principal": float(result.principal),
                "final_amount": float(result.final_amount),
                "total_interest": float(result.total_interest),
                "total_contributions": float(result.total_contributions),
                "effective_apy": float(result.effective_apy),
                "doubling_time_years": result.doubling_time,
            },
            "parameters": {
                "rate": float(result.rate),
                "years": result.years,
                "compound_frequency": result.compound_freq,
                "contribution": float(result.contribution),
                "contribution_frequency": result.contribution_freq,
            },
            "yearly_breakdown": [
                {
                    "year": snap.year,
                    "balance": float(snap.balance),
                    "interest_earned": float(snap.interest_earned),
                    "contributions_ytd": float(snap.contributions_ytd),
                    "ytd_growth_pct": snap.ytd_growth_pct,
                    "cumulative_interest": float(snap.cumulative_interest),
                }
                for snap in result.yearly_breakdown
            ],
        }

        return json.dumps(data, indent=2, cls=DecimalEncoder)
