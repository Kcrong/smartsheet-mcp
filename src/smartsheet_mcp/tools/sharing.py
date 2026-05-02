"""Sharing read tools (sheets / reports / workspaces / dashboards)."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params

_SCOPES = {"sheets", "reports", "workspaces", "sights"}


async def list_shares(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /{scope}/{id}/shares — list shares on a given resource.

    scope must be one of: sheets, reports, workspaces, sights.
    """
    scope = args["scope"]
    if scope not in _SCOPES:
        raise ValueError(f"scope must be one of {_SCOPES}, got {scope!r}")
    resource_id = args["resource_id"]
    params = pagination_params(args)
    params["sharingInclude"] = args.get("sharing_include")
    return await client.get(f"/{scope}/{resource_id}/shares", params=params)


async def get_share(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /{scope}/{id}/shares/{shareId} — single share."""
    scope = args["scope"]
    if scope not in _SCOPES:
        raise ValueError(f"scope must be one of {_SCOPES}, got {scope!r}")
    resource_id = args["resource_id"]
    share_id = args["share_id"]
    return await client.get(f"/{scope}/{resource_id}/shares/{share_id}")
