"""Sheet-related read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def list_sheets(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets — list sheets accessible to the user."""
    params = pagination_params(args)
    params["modifiedSince"] = args.get("modified_since")
    return await client.get("/sheets", params=params)


async def get_sheet(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id} — full sheet contents with optional filters."""
    sheet_id = args["sheet_id"]
    params: dict[str, Any] = {
        "include": csv(args.get("include")),
        "exclude": csv(args.get("exclude")),
        "page": args.get("page"),
        "pageSize": args.get("page_size"),
        "rowNumbers": csv(args.get("row_numbers")),
        "rowIds": csv(args.get("row_ids")),
        "columnIds": csv(args.get("column_ids")),
        "level": args.get("level"),
    }
    return await client.get(f"/sheets/{sheet_id}", params=params)


async def list_columns(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/columns — columns on a sheet."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/columns",
        params=pagination_params(args),
    )


async def get_row(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/rows/{rowId} — single row."""
    sheet_id = args["sheet_id"]
    row_id = args["row_id"]
    params: dict[str, Any] = {
        "include": csv(args.get("include")),
        "exclude": csv(args.get("exclude")),
        "level": args.get("level"),
    }
    return await client.get(f"/sheets/{sheet_id}/rows/{row_id}", params=params)
