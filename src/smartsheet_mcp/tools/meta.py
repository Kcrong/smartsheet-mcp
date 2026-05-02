"""Meta tools: server info and current user."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient


async def server_info(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /serverinfo — lists formats, feature flags, locales, etc."""
    return await client.get("/serverinfo")


async def get_user_me(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /users/me — current authenticated user profile."""
    return await client.get("/users/me")
