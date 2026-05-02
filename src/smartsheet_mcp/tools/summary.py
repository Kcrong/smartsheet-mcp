"""Sheet Summary read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def get_sheet_summary(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/summary — sheet summary (all fields)."""
    sheet_id = args["sheet_id"]
    params: dict[str, Any] = {
        "include": csv(args.get("include")),
        "exclude": csv(args.get("exclude")),
    }
    return await client.get(f"/sheets/{sheet_id}/summary", params=params)


async def list_summary_fields(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/summary/fields — summary fields with pagination."""
    sheet_id = args["sheet_id"]
    params = pagination_params(args)
    params["include"] = csv(args.get("include"))
    params["exclude"] = csv(args.get("exclude"))
    return await client.get(f"/sheets/{sheet_id}/summary/fields", params=params)
