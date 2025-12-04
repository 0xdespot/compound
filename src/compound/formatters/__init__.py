"""Formatter selection and shared types."""

from dataclasses import dataclass
from typing import Protocol

from compound.calculator import ProjectionResult


@dataclass
class RenderOptions:
    """Options controlling output rendering."""

    show_chart: bool = True
    show_table: bool = True
    quiet: bool = False  # Show only final amount


class Formatter(Protocol):
    """Protocol for output formatters."""

    def render(self, result: ProjectionResult, options: RenderOptions) -> str:
        """Render the projection result to a string."""
        ...


def get_formatter(name: str) -> Formatter:
    """Get a formatter by name.

    Args:
        name: One of 'rich', 'plain', 'json', 'csv'

    Returns:
        Formatter instance

    Raises:
        ValueError: If formatter name is unknown
    """
    name = name.lower().strip()

    if name == "rich":
        from compound.formatters.rich_fmt import RichFormatter

        return RichFormatter()

    elif name == "plain":
        from compound.formatters.plain_fmt import PlainFormatter

        return PlainFormatter()

    elif name == "json":
        from compound.formatters.json_fmt import JsonFormatter

        return JsonFormatter()

    elif name == "csv":
        from compound.formatters.csv_fmt import CsvFormatter

        return CsvFormatter()

    else:
        raise ValueError(f"Unknown formatter: {name}. Use: rich, plain, json, csv")
