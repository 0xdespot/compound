# compound

Compound interest calculator with beautiful terminal output.

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ci

# Install with rich output support (recommended)
pip install -e ".[rich]"

# Or install without rich (plain ASCII output)
pip install -e .
```

## Usage

```bash
# Basic: $10,000 at 7% for 10 years
compound 10000

# Custom rate and duration
compound 10000 -r 8% -t 30

# With monthly contributions
compound 50000 -r 7% -t 20 -c 500

# Different compounding frequency
compound 10000 -r 6% -t 10 -n quarterly

# Export to JSON
compound 10000 -o json > results.json

# Export to CSV
compound 10000 -o csv > results.csv

# Plain ASCII output (no colors)
compound 10000 -o plain

# Quiet mode (final amount only)
compound 10000 -q
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `principal` | (required) | Starting amount |
| `-r, --rate` | `7%` | Annual interest rate |
| `-t, --time` | `10` | Duration in years |
| `-n, --compound` | `monthly` | Compounding frequency |
| `-c, --contribution` | `0` | Regular contribution amount |
| `--contribution-freq` | `monthly` | Contribution frequency |
| `-o, --output` | `rich` | Output format: rich, plain, json, csv |
| `--no-chart` | — | Hide sparkline chart |
| `--no-table` | — | Hide year-by-year table |
| `-q, --quiet` | — | Show only final amount |

## Example Output

```
╭─────────────────────────────────────────────────────────────╮
│  COMPOUND INTEREST PROJECTION                               │
│  $10,000 → $19,671.51 over 10 years @ 7% (monthly)          │
╰─────────────────────────────────────────────────────────────╯

Total Interest       $9,671.51
Effective APY           7.23%
Doubling Time       9.9 years

Growth: ▁▂▂▃▄▄▅▆▇█  +96.7%

Year │   Balance   │  Interest  │  Growth  │ Cumulative
─────┼─────────────┼────────────┼──────────┼────────────
   1 │  $10,723.00 │    $723.00 │   +7.23% │    $723.00
   5 │  $14,176.25 │    $954.93 │   +7.23% │  $4,176.25
  10 │  $19,671.51 │  $1,325.39 │   +7.23% │  $9,671.51
```

## License

MIT
