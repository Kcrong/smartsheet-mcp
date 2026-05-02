"""Structure/metadata read tools (paginated children, versions, publish settings)."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


def _token_pagination(args: dict[str, Any]) -> dict[str, Any]:
    """Build token-based pagination params used by children endpoints.

    These endpoints require ``maxItems`` (100..1000, multiple of 100) and
    ``pageToken`` instead of the usual ``page``/``pageSize``.
    """
    params: dict[str, Any] = {}
    max_items = args.get("max_items")
    if max_items is not None:
        params["maxItems"] = max_items
    page_token = args.get("page_token")
    if page_token:
        params["pageToken"] = page_token
    return params


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------
async def get_folder_metadata(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /folders/{id}/metadata — lightweight folder metadata."""
    folder_id = args["folder_id"]
    return await client.get(f"/folders/{folder_id}/metadata")


async def list_folder_children(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /folders/{id}/children — paginated (token-based) child items of a folder."""
    folder_id = args["folder_id"]
    params = _token_pagination(args)
    params["include"] = csv(args.get("include"))
    return await client.get(f"/folders/{folder_id}/children", params=params)


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------
async def get_workspace_metadata(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /workspaces/{id}/metadata — lightweight workspace metadata."""
    workspace_id = args["workspace_id"]
    return await client.get(f"/workspaces/{workspace_id}/metadata")


async def list_workspace_children(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /workspaces/{id}/children — paginated (token-based) child items of a workspace."""
    workspace_id = args["workspace_id"]
    params = _token_pagination(args)
    params["include"] = csv(args.get("include"))
    return await client.get(f"/workspaces/{workspace_id}/children", params=params)


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------
async def get_sheet_version(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/version — current sheet version number."""
    sheet_id = args["sheet_id"]
    return await client.get(f"/sheets/{sheet_id}/version")


async def get_sheet_publish(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/publish — publish settings for a sheet."""
    sheet_id = args["sheet_id"]
    return await client.get(f"/sheets/{sheet_id}/publish")


async def search_in_sheet(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /search/sheets/{id} — scoped search within a single sheet."""
    sheet_id = args["sheet_id"]
    params: dict[str, Any] = {"query": args["query"]}
    return await client.get(f"/search/sheets/{sheet_id}", params=params)


# Re-export for backwards compatibility with callers that imported
# pagination_params from this module (none right now, but safe).
__all__ = [
    "get_folder_metadata",
    "list_folder_children",
    "get_workspace_metadata",
    "list_workspace_children",
    "get_sheet_version",
    "get_sheet_publish",
    "search_in_sheet",
    "pagination_params",
]
