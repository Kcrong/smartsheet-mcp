"""Attachment read tools (metadata + temporary download URLs)."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_sheet_attachments(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/attachments — all attachments on a sheet."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/attachments",
        params=pagination_params(args),
    )


async def list_row_attachments(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/rows/{rowId}/attachments — attachments on a row."""
    sheet_id = args["sheet_id"]
    row_id = args["row_id"]
    return await client.get(
        f"/sheets/{sheet_id}/rows/{row_id}/attachments",
        params=pagination_params(args),
    )


async def list_comment_attachments(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/comments/{commentId}/attachments — attachments on a comment."""
    sheet_id = args["sheet_id"]
    comment_id = args["comment_id"]
    return await client.get(
        f"/sheets/{sheet_id}/comments/{comment_id}/attachments",
        params=pagination_params(args),
    )


async def get_attachment(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/attachments/{attachmentId} — metadata + temporary download URL."""
    sheet_id = args["sheet_id"]
    attachment_id = args["attachment_id"]
    return await client.get(f"/sheets/{sheet_id}/attachments/{attachment_id}")


async def list_attachment_versions(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/attachments/{attachmentId}/versions — version history."""
    sheet_id = args["sheet_id"]
    attachment_id = args["attachment_id"]
    return await client.get(
        f"/sheets/{sheet_id}/attachments/{attachment_id}/versions",
        params=pagination_params(args),
    )
