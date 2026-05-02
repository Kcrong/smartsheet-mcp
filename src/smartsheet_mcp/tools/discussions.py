"""Discussion & comment read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def list_sheet_discussions(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/discussions — all discussions on a sheet."""
    sheet_id = args["sheet_id"]
    params = pagination_params(args)
    params["include"] = csv(args.get("include"))
    return await client.get(f"/sheets/{sheet_id}/discussions", params=params)


async def get_discussion(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/discussions/{discussionId} — single discussion."""
    sheet_id = args["sheet_id"]
    discussion_id = args["discussion_id"]
    return await client.get(f"/sheets/{sheet_id}/discussions/{discussion_id}")


async def list_row_discussions(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/rows/{rowId}/discussions — discussions on a row."""
    sheet_id = args["sheet_id"]
    row_id = args["row_id"]
    params = pagination_params(args)
    params["include"] = csv(args.get("include"))
    return await client.get(
        f"/sheets/{sheet_id}/rows/{row_id}/discussions",
        params=params,
    )


async def list_discussion_attachments(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/discussions/{discussionId}/attachments — attachments under a discussion."""
    sheet_id = args["sheet_id"]
    discussion_id = args["discussion_id"]
    params = pagination_params(args)
    return await client.get(
        f"/sheets/{sheet_id}/discussions/{discussion_id}/attachments",
        params=params,
    )


async def get_comment(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/comments/{commentId} — single comment."""
    sheet_id = args["sheet_id"]
    comment_id = args["comment_id"]
    return await client.get(f"/sheets/{sheet_id}/comments/{comment_id}")
