"""Cross-sheet reference read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_cross_sheet_references(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/crosssheetreferences — cross-sheet references."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/crosssheetreferences",
        params=pagination_params(args),
    )


async def get_cross_sheet_reference(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/crosssheetreferences/{refId} — single reference."""
    sheet_id = args["sheet_id"]
    ref_id = args["reference_id"]
    return await client.get(f"/sheets/{sheet_id}/crosssheetreferences/{ref_id}")
