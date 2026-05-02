"""Webhook read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_webhooks(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /webhooks — webhooks registered by the calling token."""
    return await client.get("/webhooks", params=pagination_params(args))


async def get_webhook(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /webhooks/{id} — single webhook."""
    webhook_id = args["webhook_id"]
    return await client.get(f"/webhooks/{webhook_id}")
