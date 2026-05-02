"""Cell-level read tools (history)."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def get_cell_history(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/rows/{rowId}/columns/{columnId}/history — change history of a cell."""
    sheet_id = args["sheet_id"]
    row_id = args["row_id"]
    column_id = args["column_id"]
    params = pagination_params(args)
    params["include"] = csv(args.get("include"))
    return await client.get(
        f"/sheets/{sheet_id}/rows/{row_id}/columns/{column_id}/history",
        params=params,
    )
