"""Pretty-print sample rows from a single Smartsheet sheet (read-only)."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from smartsheet_mcp.client import SmartsheetClient  # noqa: E402
from smartsheet_mcp.config import Settings  # noqa: E402
from smartsheet_mcp.tools import dispatch  # noqa: E402


def cell_value(cell: dict[str, Any]) -> str:
    for key in ("displayValue", "value"):
        v = cell.get(key)
        if v is not None and v != "":
            return str(v)
    return ""


def truncate(text: str, width: int) -> str:
    text = text.replace("\n", " ").replace("\r", " ")
    return text if len(text) <= width else text[: width - 1] + "…"


async def main() -> int:
    sheet_id = int(os.environ.get("SHEET_ID", "7829768520028036"))
    page_size = int(os.environ.get("PAGE_SIZE", "5"))
    max_cols = int(os.environ.get("MAX_COLS", "6"))
    col_width = int(os.environ.get("COL_WIDTH", "22"))

    settings = Settings.from_env()
    async with SmartsheetClient(settings) as client:
        sheet = await dispatch(
            client,
            "smartsheet_get_sheet",
            {"sheet_id": sheet_id, "page_size": page_size},
        )

    assert isinstance(sheet, dict)
    name = sheet.get("name") or "(unnamed sheet)"
    columns = sheet.get("columns") or []
    rows = sheet.get("rows") or []
    total_rows = sheet.get("totalRowCount")
    page = sheet.get("pageNumber")
    total_pages = sheet.get("totalPages")

    print(f"Sheet: {name}")
    print(f"  id={sheet.get('id')}  accessLevel={sheet.get('accessLevel')}")
    print(f"  permalink: {sheet.get('permalink')}")
    print(
        f"  columns={len(columns)}  rows(page)={len(rows)}  "
        f"page={page}/{total_pages}  totalRowCount={total_rows}"
    )
    print()

    shown_cols = columns[:max_cols]
    hidden = len(columns) - len(shown_cols)

    # Header
    header = " | ".join(
        truncate(c.get("title", "?"), col_width).ljust(col_width) for c in shown_cols
    )
    print(header)
    print("-" * len(header))

    # Rows
    for row in rows:
        cells_by_col = {c.get("columnId"): c for c in (row.get("cells") or [])}
        line_parts = []
        for col in shown_cols:
            cell = cells_by_col.get(col["id"], {})
            line_parts.append(truncate(cell_value(cell), col_width).ljust(col_width))
        print(" | ".join(line_parts))

    if hidden > 0:
        print(f"\n(+ {hidden} more column(s) hidden for display)")

    # Also dump the raw first row as JSON so the structure is visible
    if rows:
        print("\nRaw JSON for first row:")
        print(json.dumps(rows[0], ensure_ascii=False, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
