"""ASCII/Unicode chart generation."""

from decimal import Decimal

# Unicode block characters for sparklines (increasing height)
SPARK_BLOCKS = " ▁▂▃▄▅▆▇█"


def spark_chart(values: list[Decimal | float], width: int | None = None) -> str:
    """Generate a sparkline chart from a list of values.

    Args:
        values: List of numeric values to chart
        width: Optional width limit (will sample values if needed)

    Returns:
        String of block characters representing the values
    """
    if not values:
        return ""

    # Convert to floats
    floats = [float(v) for v in values]

    # Sample if we have more values than width
    if width and len(floats) > width:
        step = len(floats) / width
        floats = [floats[int(i * step)] for i in range(width)]

    min_val = min(floats)
    max_val = max(floats)
    range_val = max_val - min_val

    if range_val == 0:
        # All values are the same
        return SPARK_BLOCKS[4] * len(floats)

    # Map each value to a block character
    result = []
    for v in floats:
        # Normalize to 0-1 range
        normalized = (v - min_val) / range_val
        # Map to block index (0-8)
        index = int(normalized * (len(SPARK_BLOCKS) - 1))
        result.append(SPARK_BLOCKS[index])

    return "".join(result)


def bar_chart(
    labels: list[str],
    values: list[Decimal | float],
    width: int = 30,
    fill_char: str = "█",
    empty_char: str = "░",
    show_values: bool = True,
    value_formatter: callable = None,
) -> str:
    """Generate a horizontal bar chart.

    Args:
        labels: Row labels (e.g., "Year 1", "Year 5")
        values: Corresponding values
        width: Width of the bar portion
        fill_char: Character for filled portion
        empty_char: Character for empty portion
        show_values: Whether to show value at end of bar
        value_formatter: Optional function to format values

    Returns:
        Multi-line string with the bar chart
    """
    if not values or not labels:
        return ""

    if value_formatter is None:
        value_formatter = lambda x: f"${float(x):,.0f}"

    # Convert to floats
    floats = [float(v) for v in values]
    max_val = max(floats)

    # Find max label width for alignment
    max_label_width = max(len(label) for label in labels)

    lines = []
    for label, value in zip(labels, floats):
        # Calculate bar fill
        if max_val > 0:
            fill_width = int((value / max_val) * width)
        else:
            fill_width = 0

        empty_width = width - fill_width

        # Build the line
        bar = fill_char * fill_width + empty_char * empty_width

        if show_values:
            formatted_value = value_formatter(value)
            line = f"{label:<{max_label_width}}  {bar}  {formatted_value}"
        else:
            line = f"{label:<{max_label_width}}  {bar}"

        lines.append(line)

    return "\n".join(lines)


def growth_summary(start: Decimal | float, end: Decimal | float) -> str:
    """Generate a growth summary line with sparkline placeholder.

    Args:
        start: Starting value
        end: Ending value

    Returns:
        Formatted growth string like "Growth: +96.7%"
    """
    start_f = float(start)
    end_f = float(end)

    if start_f == 0:
        return "Growth: N/A (started at $0)"

    pct_change = ((end_f - start_f) / start_f) * 100
    sign = "+" if pct_change >= 0 else ""

    return f"Growth: {sign}{pct_change:.1f}%"
