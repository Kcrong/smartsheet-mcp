"""Template & Favorites read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_templates(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /templates — user's custom templates (deprecated but still returns data)."""
    return await client.get("/templates", params=pagination_params(args))


async def list_public_templates(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /templates/public — public Solution Center templates."""
    return await client.get("/templates/public", params=pagination_params(args))


async def list_favorites(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /favorites — user's favorite items."""
    return await client.get("/favorites", params=pagination_params(args))


async def get_favorite(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /favorites/{type}/{id} — check a specific item's favorite status."""
    fav_type = args["favorite_type"]
    fav_id = args["favorite_id"]
    return await client.get(f"/favorites/{fav_type}/{fav_id}")
