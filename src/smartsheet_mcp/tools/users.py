"""User, group, contact and alternate email read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import csv, pagination_params


async def list_users(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /users — list users in the user's account (admin-ish)."""
    params = pagination_params(args)
    params["email"] = csv(args.get("emails"))
    params["includeAll"] = "true" if args.get("include_all") else None
    return await client.get("/users", params=params)


async def get_user(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /users/{id} — single user."""
    user_id = args["user_id"]
    return await client.get(f"/users/{user_id}")


async def list_groups(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /groups — list groups in the user's account."""
    return await client.get("/groups", params=pagination_params(args))


async def get_group(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /groups/{id} — single group with members."""
    group_id = args["group_id"]
    return await client.get(f"/groups/{group_id}")


async def list_contacts(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /contacts — list the authenticated user's Smartsheet contacts."""
    return await client.get("/contacts", params=pagination_params(args))


async def get_contact(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /contacts/{id} — single contact."""
    contact_id = args["contact_id"]
    return await client.get(f"/contacts/{contact_id}")


async def list_alternate_emails(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /users/{id}/alternateemails — all alt emails for a user."""
    user_id = args["user_id"]
    return await client.get(
        f"/users/{user_id}/alternateemails",
        params=pagination_params(args),
    )


async def get_alternate_email(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /users/{id}/alternateemails/{altId} — single alt email."""
    user_id = args["user_id"]
    alt_id = args["alternate_email_id"]
    return await client.get(f"/users/{user_id}/alternateemails/{alt_id}")
