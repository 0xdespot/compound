"""CSV formatter for spreadsheet export."""

import csv
from io import StringIO

from compound.calculator import ProjectionResult
from compound.formatters import RenderOptions


class CsvFormatter:
    """Formatter that outputs CSV."""

    def render(self, result: ProjectionResult, options: RenderOptions) -> str:
        """Render projection as CSV."""
        output = StringIO()
        writer = csv.writer(output)

        if options.quiet:
            writer.writerow(["final_amount"])
            writer.writerow([float(result.final_amount)])
            return output.getvalue()

        # Header
        writer.writerow(
            [
                "year",
                "balance",
                "interest_earned",
                "contributions_ytd",
                "ytd_growth_pct",
                "cumulative_interest",
            ]
        )

        # Data rows
        for snap in result.yearly_breakdown:
            writer.writerow(
                [
                    snap.year,
                    float(snap.balance),
                    float(snap.interest_earned),
                    float(snap.contributions_ytd),
                    snap.ytd_growth_pct,
                    float(snap.cumulative_interest),
                ]
            )

        return output.getvalue()
