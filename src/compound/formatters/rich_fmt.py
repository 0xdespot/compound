"""Rich library formatter for beautiful terminal output."""

from compound.calculator import ProjectionResult
from compound.formatters import RenderOptions
from compound.utils import format_currency, format_percent
from compound.charts import spark_chart

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichFormatter:
    """Formatter using the rich library for beautiful output."""

    def __init__(self):
        if not RICH_AVAILABLE:
            # Fallback to plain formatter if rich is not installed
            from compound.formatters.plain_fmt import PlainFormatter

            self._fallback = PlainFormatter()
        else:
            self._fallback = None
            self._console = Console()

    def render(self, result: ProjectionResult, options: RenderOptions) -> str:
        """Render projection with rich formatting."""
        if self._fallback:
            return self._fallback.render(result, options)

        if options.quiet:
            return format_currency(result.final_amount)

        # Build output by capturing rich console output
        from io import StringIO

        string_buffer = StringIO()
        console = Console(file=string_buffer, force_terminal=True)

        # Header panel
        console.print(self._render_header(result))
        console.print()

        # Metrics table
        console.print(self._render_metrics(result))
        console.print()

        # Sparkline
        if options.show_chart and result.yearly_breakdown:
            balances = [snap.balance for snap in result.yearly_breakdown]
            spark = spark_chart(balances)
            total_growth = (
                (float(result.final_amount) - float(result.principal))
                / float(result.principal)
                * 100
            )
            growth_text = Text()
            growth_text.append("Growth: ", style="bold")
            growth_text.append(spark, style="green")
            growth_text.append(f"  +{total_growth:.1f}%", style="bold green")
            console.print(growth_text)
            console.print()

        # Year-by-year table
        if options.show_table and result.yearly_breakdown:
            console.print(self._render_table(result))

        return string_buffer.getvalue()

    def _render_header(self, result: ProjectionResult) -> Panel:
        """Render the summary header panel."""
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
            summary = f"[bold cyan]{principal_str}[/] + [cyan]{contrib_str}/{contrib_freq}[/] [dim]→[/] [bold green]{final_str}[/] over [bold]{result.years}[/] years @ [bold]{rate_str}[/] [dim]({freq_name})[/]"
        else:
            summary = f"[bold cyan]{principal_str}[/] [dim]→[/] [bold green]{final_str}[/] over [bold]{result.years}[/] years @ [bold]{rate_str}[/] [dim]({freq_name})[/]"

        return Panel(
            summary,
            title="[bold]COMPOUND INTEREST PROJECTION[/]",
            border_style="blue",
        )

    def _render_metrics(self, result: ProjectionResult) -> Table:
        """Render the key metrics table."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right", style="bold")

        if result.total_contributions > 0:
            table.add_row(
                "Starting Principal", format_currency(result.principal), style="cyan"
            )
            table.add_row(
                "Total Contributions",
                format_currency(result.total_contributions),
                style="cyan",
            )

        table.add_row(
            "Total Interest", format_currency(result.total_interest), style="green"
        )
        table.add_row("Effective APY", format_percent(result.effective_apy))
        table.add_row("Doubling Time", f"{result.doubling_time} years")

        return table

    def _render_table(self, result: ProjectionResult) -> Table:
        """Render the year-by-year breakdown table."""
        # Determine which years to show
        breakdown = result.yearly_breakdown
        if len(breakdown) <= 10:
            rows = breakdown
        else:
            indices = [0]
            for y in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
                if y <= result.years:
                    indices.append(y - 1)
            if result.years - 1 not in indices:
                indices.append(result.years - 1)
            rows = [breakdown[i] for i in sorted(set(indices))]

        # Build table
        has_contributions = result.contribution > 0

        table = Table(title="Year-by-Year Breakdown", border_style="dim")
        table.add_column("Year", justify="right", style="dim")
        table.add_column("Balance", justify="right", style="green")
        table.add_column("Interest", justify="right", style="cyan")

        if has_contributions:
            table.add_column("Contributions", justify="right", style="yellow")
        else:
            table.add_column("Growth", justify="right")

        table.add_column("Cumulative", justify="right", style="bold")

        for snap in rows:
            if has_contributions:
                table.add_row(
                    str(snap.year),
                    format_currency(snap.balance),
                    format_currency(snap.interest_earned),
                    format_currency(snap.contributions_ytd),
                    format_currency(snap.cumulative_interest),
                )
            else:
                table.add_row(
                    str(snap.year),
                    format_currency(snap.balance),
                    format_currency(snap.interest_earned),
                    f"+{snap.ytd_growth_pct:.2f}%",
                    format_currency(snap.cumulative_interest),
                )

        return table
