"""Automation rule read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_automation_rules(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/automationrules — automation rules on a sheet."""
    sheet_id = args["sheet_id"]
    return await client.get(
        f"/sheets/{sheet_id}/automationrules",
        params=pagination_params(args),
    )


async def get_automation_rule(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/automationrules/{ruleId} — single automation rule."""
    sheet_id = args["sheet_id"]
    rule_id = args["rule_id"]
    return await client.get(f"/sheets/{sheet_id}/automationrules/{rule_id}")
