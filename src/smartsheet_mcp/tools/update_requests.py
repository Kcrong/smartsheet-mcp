"""Update request read tools (pending and sent)."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_update_requests(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/updaterequests — pending update requests."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/updaterequests",
        params=pagination_params(args),
    )


async def get_update_request(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/updaterequests/{id} — single update request."""
    sheet_id = args["sheet_id"]
    ur_id = args["update_request_id"]
    return await client.get(f"/sheets/{sheet_id}/updaterequests/{ur_id}")


async def list_sent_update_requests(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/sentupdaterequests — already-sent update requests."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/sentupdaterequests",
        params=pagination_params(args),
    )


async def get_sent_update_request(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/sentupdaterequests/{id} — single sent update request."""
    sheet_id = args["sheet_id"]
    sur_id = args["sent_update_request_id"]
    return await client.get(f"/sheets/{sheet_id}/sentupdaterequests/{sur_id}")
