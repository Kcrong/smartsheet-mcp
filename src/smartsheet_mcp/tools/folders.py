"""Folder-related read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv


async def list_personal_folders(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /folders/personal — top-level contents of the user's Home."""
    return await client.get("/folders/personal")


async def get_folder(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /folders/{id} — folder contents."""
    folder_id = args["folder_id"]
    params: dict[str, Any] = {"include": csv(args.get("include"))}
    return await client.get(f"/folders/{folder_id}", params=params)
