"""Dashboard (Sight) read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_dashboards(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sights — list dashboards."""
    params = pagination_params(args)
    params["modifiedSince"] = args.get("modified_since")
    return await client.get("/sights", params=params)


async def get_dashboard(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sights/{id} — full dashboard with widgets."""
    sight_id = args["dashboard_id"]
    return await client.get(f"/sights/{sight_id}")


async def get_dashboard_publish(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sights/{id}/publish — publish settings."""
    sight_id = args["dashboard_id"]
    return await client.get(f"/sights/{sight_id}/publish")
