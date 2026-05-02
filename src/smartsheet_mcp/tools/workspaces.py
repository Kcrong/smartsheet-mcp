"""Workspace-related read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def list_workspaces(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /workspaces — list workspaces the user can access."""
    return await client.get("/workspaces", params=pagination_params(args))


async def get_workspace(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /workspaces/{id} — workspace contents."""
    workspace_id = args["workspace_id"]
    params: dict[str, Any] = {"include": csv(args.get("include"))}
    if args.get("load_all"):
        params["loadAll"] = "true"
    return await client.get(f"/workspaces/{workspace_id}", params=params)
