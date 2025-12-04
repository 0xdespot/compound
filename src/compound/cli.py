"""Command-line interface for compound interest calculator."""

import argparse
import sys
from decimal import Decimal, InvalidOperation

from compound import __version__
from compound.calculator import calculate_compound_interest
from compound.formatters import get_formatter, RenderOptions
from compound.utils import parse_rate, parse_frequency


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="compound",
        description="Calculate compound interest with beautiful output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  compound 10000                         # $10k at 7% for 10 years
  compound 10000 -r 8% -t 30             # Custom rate and time
  compound 50000 -c 500                  # With $500/month contributions
  compound 10000 -o json > results.json  # Export to JSON
        """,
    )

    parser.add_argument(
        "principal",
        type=str,
        help="Starting principal amount (e.g., 10000 or 10,000)",
    )

    parser.add_argument(
        "-r",
        "--rate",
        type=str,
        default="7%",
        help="Annual interest rate (default: 7%%). Accepts: 7%%, 0.07, .07",
    )

    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=10,
        help="Duration in years (default: 10)",
    )

    parser.add_argument(
        "-n",
        "--compound",
        type=str,
        default="monthly",
        help="Compounding frequency: daily, monthly, quarterly, annually, or integer (default: monthly)",
    )

    parser.add_argument(
        "-c",
        "--contribution",
        type=str,
        default="0",
        help="Regular contribution amount (default: 0)",
    )

    parser.add_argument(
        "--contribution-freq",
        type=str,
        default="monthly",
        help="Contribution frequency: monthly, weekly, annually, etc. (default: monthly)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="rich",
        choices=["rich", "plain", "json", "csv"],
        help="Output format (default: rich)",
    )

    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Suppress sparkline chart",
    )

    parser.add_argument(
        "--no-table",
        action="store_true",
        help="Suppress year-by-year table",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Show only final amount",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def parse_amount(value: str) -> Decimal:
    """Parse an amount string, allowing commas and currency symbols."""
    # Remove currency symbols, commas, spaces
    cleaned = value.replace("$", "").replace(",", "").replace(" ", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Invalid amount: {value}")


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Parse inputs
    try:
        principal = parse_amount(args.principal)
        if principal < 0:
            print("Error: Principal cannot be negative.", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        rate = parse_rate(args.rate)
        if rate > 1:
            print(
                f"Warning: Rate {float(rate)*100:.1f}% seems high. Did you mean {args.rate}?",
                file=sys.stderr,
            )
    except (ValueError, InvalidOperation) as e:
        print(f"Error parsing rate: {e}", file=sys.stderr)
        return 1

    try:
        compound_freq = parse_frequency(args.compound)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        contribution = parse_amount(args.contribution)
        if contribution < 0:
            print("Error: Contribution cannot be negative.", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"Error parsing contribution: {e}", file=sys.stderr)
        return 1

    try:
        contribution_freq = parse_frequency(args.contribution_freq)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.time <= 0:
        print("Error: Time must be positive.", file=sys.stderr)
        return 1

    # Calculate
    result = calculate_compound_interest(
        principal=principal,
        rate=rate,
        years=args.time,
        compound_freq=compound_freq,
        contribution=contribution,
        contribution_freq=contribution_freq,
    )

    # Render output
    try:
        formatter = get_formatter(args.output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    options = RenderOptions(
        show_chart=not args.no_chart,
        show_table=not args.no_table,
        quiet=args.quiet,
    )

    output = formatter.render(result, options)
    print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
