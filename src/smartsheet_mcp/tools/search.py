"""Global search across the user's Smartsheet items."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv


async def search(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /search — global search across accessible items."""
    params: dict[str, Any] = {
        "query": args["query"],
        "location": args.get("location"),
        "include": csv(args.get("include")),
        "scopes": csv(args.get("scopes")),
        "modifiedSince": args.get("modified_since"),
    }
    return await client.get("/search", params=params)
