"""Report-related read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def list_reports(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /reports — list reports accessible to the user."""
    params = pagination_params(args)
    params["modifiedSince"] = args.get("modified_since")
    return await client.get("/reports", params=params)


async def get_report(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /reports/{id} — full report contents."""
    report_id = args["report_id"]
    params: dict[str, Any] = {
        "include": csv(args.get("include")),
        "page": args.get("page"),
        "pageSize": args.get("page_size"),
        "level": args.get("level"),
    }
    return await client.get(f"/reports/{report_id}", params=params)


async def get_report_publish(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /reports/{id}/publish — publish settings."""
    report_id = args["report_id"]
    return await client.get(f"/reports/{report_id}/publish")
