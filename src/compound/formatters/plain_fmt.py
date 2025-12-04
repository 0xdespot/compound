"""Plain text formatter using ASCII characters."""

from compound.calculator import ProjectionResult
from compound.formatters import RenderOptions
from compound.utils import format_currency, format_percent
from compound.charts import spark_chart, bar_chart


class PlainFormatter:
    """ASCII-only plain text formatter."""

    def render(self, result: ProjectionResult, options: RenderOptions) -> str:
        """Render projection as plain ASCII text."""
        if options.quiet:
            return format_currency(result.final_amount)

        lines = []

        # Header
        lines.append(self._render_header(result))
        lines.append("")

        # Metrics panel
        lines.append(self._render_metrics(result))
        lines.append("")

        # Sparkline
        if options.show_chart and result.yearly_breakdown:
            balances = [snap.balance for snap in result.yearly_breakdown]
            spark = spark_chart(balances)
            total_growth = (
                (float(result.final_amount) - float(result.principal))
                / float(result.principal)
                * 100
            )
            lines.append(f"Growth: {spark}  +{total_growth:.1f}%")
            lines.append("")

        # Year-by-year table
        if options.show_table and result.yearly_breakdown:
            lines.append(self._render_table(result))

        return "\n".join(lines)

    def _render_header(self, result: ProjectionResult) -> str:
        """Render the summary header box."""
        # Build summary line
        principal_str = format_currency(result.principal)
        final_str = format_currency(result.final_amount)
        rate_str = format_percent(result.rate)

        freq_names = {1: "annually", 4: "quarterly", 12: "monthly", 365: "daily"}
        freq_name = freq_names.get(result.compound_freq, f"{result.compound_freq}x/yr")

        if result.contribution > 0:
            contrib_str = format_currency(result.contribution)
            contrib_freq = {1: "yr", 12: "mo", 26: "2wk", 52: "wk"}.get(
                result.contribution_freq, ""
            )
            summary = f"{principal_str} + {contrib_str}/{contrib_freq} -> {final_str} over {result.years} years @ {rate_str} ({freq_name})"
        else:
            summary = f"{principal_str} -> {final_str} over {result.years} years @ {rate_str} ({freq_name})"

        # Box it
        width = max(len(summary) + 4, 50)
        border = "+" + "-" * (width - 2) + "+"
        title = "COMPOUND INTEREST PROJECTION"
        title_line = f"|  {title:<{width - 4}}|"
        summary_line = f"|  {summary:<{width - 4}}|"

        return "\n".join([border, title_line, summary_line, border])

    def _render_metrics(self, result: ProjectionResult) -> str:
        """Render the key metrics panel."""
        metrics = [
            ("Total Interest", format_currency(result.total_interest)),
            ("Effective APY", format_percent(result.effective_apy)),
            ("Doubling Time", f"{result.doubling_time} years"),
        ]

        if result.total_contributions > 0:
            metrics.insert(
                1, ("Total Contributions", format_currency(result.total_contributions))
            )

        # Find max widths
        label_width = max(len(m[0]) for m in metrics)
        value_width = max(len(m[1]) for m in metrics)
        total_width = label_width + value_width + 7

        lines = ["+" + "-" * (total_width - 2) + "+"]
        for label, value in metrics:
            lines.append(f"| {label:<{label_width}} | {value:>{value_width}} |")
        lines.append("+" + "-" * (total_width - 2) + "+")

        return "\n".join(lines)

    def _render_table(self, result: ProjectionResult) -> str:
        """Render the year-by-year breakdown table."""
        # Determine which years to show
        breakdown = result.yearly_breakdown
        if len(breakdown) <= 10:
            rows = breakdown
        else:
            # Show years 1, 5, 10, 15, 20, ... and final year
            indices = [0]  # Year 1
            for y in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
                if y <= result.years:
                    indices.append(y - 1)
            if result.years - 1 not in indices:
                indices.append(result.years - 1)
            rows = [breakdown[i] for i in sorted(set(indices))]

        # Build table
        has_contributions = result.contribution > 0

        if has_contributions:
            header = "Year |    Balance    |   Interest   | Contributions | Cumulative"
            sep = "-----|---------------|--------------|---------------|------------"
        else:
            header = "Year |    Balance    |   Interest   |  Growth  | Cumulative"
            sep = "-----|---------------|--------------|----------|------------"

        lines = [header, sep]

        for snap in rows:
            if has_contributions:
                line = (
                    f"{snap.year:>4} | "
                    f"{format_currency(snap.balance):>13} | "
                    f"{format_currency(snap.interest_earned):>12} | "
                    f"{format_currency(snap.contributions_ytd):>13} | "
                    f"{format_currency(snap.cumulative_interest):>10}"
                )
            else:
                line = (
                    f"{snap.year:>4} | "
                    f"{format_currency(snap.balance):>13} | "
                    f"{format_currency(snap.interest_earned):>12} | "
                    f"{snap.ytd_growth_pct:>7.2f}% | "
                    f"{format_currency(snap.cumulative_interest):>10}"
                )
            lines.append(line)

        return "\n".join(lines)
