from __future__ import annotations

import json
from typing import Any

from django_delete_preview.collector import DeleteSummary


def format_as_text(summary: DeleteSummary, include_items: bool = True) -> str:
    """
    Format a DeleteSummary as a human-readable text block.

    Args:
        summary: The DeleteSummary to format.
        include_items: Whether to include individual object representations.

    Returns:
        A formatted multi-line string.
    """
    lines: list[str] = [
        f"Database    : {summary['database']}",
        f"Total items : {summary['total_objects']}",
        "",
        "Models affected:",
    ]
    for model_label, count in summary["models"].items():
        lines.append(f"  {model_label}: {count}")

    if include_items and summary.get("items"):
        lines.append("")
        lines.append("Items:")
        for model_label, item_list in summary["items"].items():
            lines.append(f"  {model_label}:")
            for item in item_list:
                lines.append(f"    - {item}")

    return "\n".join(lines)


def format_as_json(
    summary: DeleteSummary,
    include_items: bool = False,
    indent: int | None = 2,
) -> str:
    """
    Format a DeleteSummary as a JSON string.

    Args:
        summary: The DeleteSummary to format.
        include_items: Whether to include individual object representations.
        indent: JSON indentation level (None for compact output).

    Returns:
        A JSON string.
    """
    data: dict[str, Any] = {
        "database": summary["database"],
        "total_objects": summary["total_objects"],
        "models": summary["models"],
    }
    if include_items:
        data["items"] = summary["items"]

    return json.dumps(data, indent=indent, ensure_ascii=False)
