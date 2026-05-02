"""Tool catalog and dispatcher for the Smartsheet MCP server.

Read-only tools mirror the Smartsheet REST API. Each tool has:
  - a JSON Schema describing its arguments, and
  - a handler coroutine that maps those arguments to an HTTP call.

All tool names are ``smartsheet_<snake_case>``.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from mcp.types import Tool

from ..client import SmartsheetClient
from . import (
    attachments,
    automation,
    cells,
    cross_sheet,
    dashboards,
    discussions,
    extras,
    folders,
    meta,
    proofs,
    reports,
    search,
    sharing,
    sheets,
    structure,
    summary,
    update_requests,
    users,
    webhooks,
    workspaces,
)

Handler = Callable[[SmartsheetClient, dict[str, Any]], Awaitable[Any]]


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------
_ID_TYPE = {"type": ["integer", "string"]}
_PAGINATION = {
    "include_all": {
        "type": "boolean",
        "description": "If true, return all results (ignores page/page_size).",
    },
    "page": {"type": "integer", "minimum": 1, "description": "1-based page number."},
    "page_size": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10000,
        "description": "Results per page.",
    },
}


def _schema(
    properties: dict[str, Any] | None = None,
    *,
    required: list[str] | None = None,
    pagination: bool = False,
) -> dict[str, Any]:
    props: dict[str, Any] = {}
    if pagination:
        props.update(_PAGINATION)
    if properties:
        props.update(properties)
    schema: dict[str, Any] = {
        "type": "object",
        "properties": props,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


def _tool(name: str, description: str, schema: dict[str, Any]) -> Tool:
    return Tool(name=name, description=description, inputSchema=schema)


# ---------------------------------------------------------------------------
# Arg schemas reused across tools
# ---------------------------------------------------------------------------
_SHEET_ID_ARG = {"sheet_id": {**_ID_TYPE, "description": "Smartsheet sheet ID."}}
_ROW_ID_ARG = {"row_id": {**_ID_TYPE, "description": "Row ID inside the sheet."}}
_INCLUDE_ARG = {
    "include": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional include flags.",
    }
}
_EXCLUDE_ARG = {
    "exclude": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional exclude flags.",
    }
}


# ---------------------------------------------------------------------------
# Tool catalog
# ---------------------------------------------------------------------------
TOOLS: list[Tool] = [
    # -------------------- Meta --------------------
    _tool(
        "smartsheet_server_info",
        "Get Smartsheet server information (formats, feature flags). Useful as a connectivity / auth smoke test.",
        _schema(),
    ),
    _tool(
        "smartsheet_get_user_me",
        "Get the currently authenticated Smartsheet user's profile.",
        _schema(),
    ),
    # -------------------- Sheets / Columns / Rows --------------------
    _tool(
        "smartsheet_list_sheets",
        "List sheets the authenticated user has access to.",
        _schema(
            {"modified_since": {"type": "string", "description": "ISO-8601 timestamp filter."}},
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_sheet",
        "Get a sheet's full contents (columns + rows + cells). Use pagination for large sheets.",
        _schema(
            {
                **_SHEET_ID_ARG,
                **_INCLUDE_ARG,
                **_EXCLUDE_ARG,
                "page": _PAGINATION["page"],
                "page_size": _PAGINATION["page_size"],
                "row_numbers": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Only these row numbers (1-based).",
                },
                "row_ids": {
                    "type": "array",
                    "items": _ID_TYPE,
                    "description": "Only these row IDs.",
                },
                "column_ids": {
                    "type": "array",
                    "items": _ID_TYPE,
                    "description": "Only these column IDs.",
                },
                "level": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "API response level (e.g. 2 for multi-contact).",
                },
            },
            required=["sheet_id"],
        ),
    ),
    _tool(
        "smartsheet_list_columns",
        "List columns defined on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_row",
        "Get a specific row from a sheet.",
        _schema(
            {
                **_SHEET_ID_ARG,
                **_ROW_ID_ARG,
                **_INCLUDE_ARG,
                **_EXCLUDE_ARG,
                "level": {"type": "integer", "minimum": 0},
            },
            required=["sheet_id", "row_id"],
        ),
    ),
    _tool(
        "smartsheet_get_sheet_version",
        "Get a sheet's current version number (lightweight).",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"]),
    ),
    _tool(
        "smartsheet_get_sheet_publish",
        "Get a sheet's publish settings.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"]),
    ),
    # -------------------- Cells --------------------
    _tool(
        "smartsheet_get_cell_history",
        "Get the change history of a single cell (row x column).",
        _schema(
            {
                **_SHEET_ID_ARG,
                **_ROW_ID_ARG,
                "column_id": {**_ID_TYPE, "description": "Column ID."},
                **_INCLUDE_ARG,
            },
            required=["sheet_id", "row_id", "column_id"],
            pagination=True,
        ),
    ),
    # -------------------- Sheet Summary --------------------
    _tool(
        "smartsheet_get_sheet_summary",
        "Get a sheet's summary (all custom summary fields).",
        _schema({**_SHEET_ID_ARG, **_INCLUDE_ARG, **_EXCLUDE_ARG}, required=["sheet_id"]),
    ),
    _tool(
        "smartsheet_list_summary_fields",
        "List a sheet's summary fields with pagination.",
        _schema(
            {**_SHEET_ID_ARG, **_INCLUDE_ARG, **_EXCLUDE_ARG},
            required=["sheet_id"],
            pagination=True,
        ),
    ),
    # -------------------- Search --------------------
    _tool(
        "smartsheet_search",
        "Search across all Smartsheet items the user can access.",
        _schema(
            {
                "query": {"type": "string", "minLength": 1, "description": "Search query string."},
                "location": {
                    "type": "string",
                    "description": "Set to 'personalWorkspace' to limit scope.",
                },
                **_INCLUDE_ARG,
                "scopes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Restrict to specific scopes.",
                },
                "modified_since": {"type": "string"},
            },
            required=["query"],
        ),
    ),
    _tool(
        "smartsheet_search_in_sheet",
        "Search within a single sheet only.",
        _schema(
            {
                **_SHEET_ID_ARG,
                "query": {"type": "string", "minLength": 1},
            },
            required=["sheet_id", "query"],
        ),
    ),
    # -------------------- Workspaces --------------------
    _tool(
        "smartsheet_list_workspaces",
        "List workspaces the user can access.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_get_workspace",
        "Get a workspace and its top-level contents.",
        _schema(
            {
                "workspace_id": {**_ID_TYPE, "description": "Workspace ID."},
                **_INCLUDE_ARG,
                "load_all": {
                    "type": "boolean",
                    "description": "Recursively include nested contents.",
                },
            },
            required=["workspace_id"],
        ),
    ),
    _tool(
        "smartsheet_get_workspace_metadata",
        "Lightweight metadata for a workspace.",
        _schema({"workspace_id": {**_ID_TYPE}}, required=["workspace_id"]),
    ),
    _tool(
        "smartsheet_list_workspace_children",
        "Paginated child items (folders/sheets/reports/dashboards/templates) of a workspace. "
        "Uses token-based pagination: max_items must be 100..1000 (multiple of 100).",
        _schema(
            {
                "workspace_id": {**_ID_TYPE},
                **_INCLUDE_ARG,
                "max_items": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 1000,
                    "multipleOf": 100,
                    "description": "Max items per page (100..1000, multiple of 100).",
                },
                "page_token": {
                    "type": "string",
                    "description": "Cursor from a previous response's nextToken.",
                },
            },
            required=["workspace_id"],
        ),
    ),
    # -------------------- Folders --------------------
    _tool(
        "smartsheet_list_personal_folders",
        "List the top-level items in the user's Home.",
        _schema(),
    ),
    _tool(
        "smartsheet_get_folder",
        "Get a folder and its contents.",
        _schema(
            {"folder_id": {**_ID_TYPE}, **_INCLUDE_ARG},
            required=["folder_id"],
        ),
    ),
    _tool(
        "smartsheet_get_folder_metadata",
        "Lightweight metadata for a folder.",
        _schema({"folder_id": {**_ID_TYPE}}, required=["folder_id"]),
    ),
    _tool(
        "smartsheet_list_folder_children",
        "Paginated child items of a folder. "
        "Uses token-based pagination: max_items must be 100..1000 (multiple of 100).",
        _schema(
            {
                "folder_id": {**_ID_TYPE},
                **_INCLUDE_ARG,
                "max_items": {
                    "type": "integer",
                    "minimum": 100,
                    "maximum": 1000,
                    "multipleOf": 100,
                    "description": "Max items per page (100..1000, multiple of 100).",
                },
                "page_token": {
                    "type": "string",
                    "description": "Cursor from a previous response's nextToken.",
                },
            },
            required=["folder_id"],
        ),
    ),
    # -------------------- Reports --------------------
    _tool(
        "smartsheet_list_reports",
        "List reports the user can access.",
        _schema({"modified_since": {"type": "string"}}, pagination=True),
    ),
    _tool(
        "smartsheet_get_report",
        "Get a report with columns/rows.",
        _schema(
            {
                "report_id": {**_ID_TYPE},
                **_INCLUDE_ARG,
                "page": _PAGINATION["page"],
                "page_size": _PAGINATION["page_size"],
                "level": {"type": "integer", "minimum": 0},
            },
            required=["report_id"],
        ),
    ),
    _tool(
        "smartsheet_get_report_publish",
        "Get a report's publish settings.",
        _schema({"report_id": {**_ID_TYPE}}, required=["report_id"]),
    ),
    # -------------------- Dashboards (Sights) --------------------
    _tool(
        "smartsheet_list_dashboards",
        "List dashboards (Sights) the user can access.",
        _schema({"modified_since": {"type": "string"}}, pagination=True),
    ),
    _tool(
        "smartsheet_get_dashboard",
        "Get a dashboard (with its widgets).",
        _schema({"dashboard_id": {**_ID_TYPE}}, required=["dashboard_id"]),
    ),
    _tool(
        "smartsheet_get_dashboard_publish",
        "Get a dashboard's publish settings.",
        _schema({"dashboard_id": {**_ID_TYPE}}, required=["dashboard_id"]),
    ),
    # -------------------- Discussions & Comments --------------------
    _tool(
        "smartsheet_list_sheet_discussions",
        "List all discussions on a sheet.",
        _schema(
            {**_SHEET_ID_ARG, **_INCLUDE_ARG},
            required=["sheet_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_discussion",
        "Get a single discussion with comments.",
        _schema(
            {
                **_SHEET_ID_ARG,
                "discussion_id": {**_ID_TYPE},
            },
            required=["sheet_id", "discussion_id"],
        ),
    ),
    _tool(
        "smartsheet_list_row_discussions",
        "List discussions on a specific row.",
        _schema(
            {**_SHEET_ID_ARG, **_ROW_ID_ARG, **_INCLUDE_ARG},
            required=["sheet_id", "row_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_list_discussion_attachments",
        "List attachments under a discussion.",
        _schema(
            {**_SHEET_ID_ARG, "discussion_id": {**_ID_TYPE}},
            required=["sheet_id", "discussion_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_comment",
        "Get a single comment.",
        _schema(
            {**_SHEET_ID_ARG, "comment_id": {**_ID_TYPE}},
            required=["sheet_id", "comment_id"],
        ),
    ),
    # -------------------- Attachments --------------------
    _tool(
        "smartsheet_list_sheet_attachments",
        "List all attachments on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_list_row_attachments",
        "List attachments on a row.",
        _schema({**_SHEET_ID_ARG, **_ROW_ID_ARG}, required=["sheet_id", "row_id"], pagination=True),
    ),
    _tool(
        "smartsheet_list_comment_attachments",
        "List attachments on a comment.",
        _schema(
            {**_SHEET_ID_ARG, "comment_id": {**_ID_TYPE}},
            required=["sheet_id", "comment_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_attachment",
        "Get an attachment's metadata and temporary download URL.",
        _schema(
            {**_SHEET_ID_ARG, "attachment_id": {**_ID_TYPE}},
            required=["sheet_id", "attachment_id"],
        ),
    ),
    _tool(
        "smartsheet_list_attachment_versions",
        "List version history of an attachment.",
        _schema(
            {**_SHEET_ID_ARG, "attachment_id": {**_ID_TYPE}},
            required=["sheet_id", "attachment_id"],
            pagination=True,
        ),
    ),
    # -------------------- Users / Groups / Contacts / Alt Emails --------------------
    _tool(
        "smartsheet_list_users",
        "List users in the authenticated user's account (admin rights may be required).",
        _schema(
            {
                "emails": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by email(s).",
                },
            },
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_user",
        "Get a single user.",
        _schema({"user_id": {**_ID_TYPE}}, required=["user_id"]),
    ),
    _tool(
        "smartsheet_list_groups",
        "List groups in the user's account.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_get_group",
        "Get a single group (includes members).",
        _schema({"group_id": {**_ID_TYPE}}, required=["group_id"]),
    ),
    _tool(
        "smartsheet_list_contacts",
        "List the authenticated user's Smartsheet contacts.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_get_contact",
        "Get a single contact.",
        _schema({"contact_id": {"type": "string"}}, required=["contact_id"]),
    ),
    _tool(
        "smartsheet_list_alternate_emails",
        "List a user's alternate email addresses (Enterprise feature).",
        _schema({"user_id": {**_ID_TYPE}}, required=["user_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_alternate_email",
        "Get a single alternate email for a user.",
        _schema(
            {
                "user_id": {**_ID_TYPE},
                "alternate_email_id": {**_ID_TYPE},
            },
            required=["user_id", "alternate_email_id"],
        ),
    ),
    # -------------------- Sharing --------------------
    _tool(
        "smartsheet_list_shares",
        "List shares for a sheet/report/workspace/dashboard.",
        _schema(
            {
                "scope": {"type": "string", "enum": ["sheets", "reports", "workspaces", "sights"]},
                "resource_id": {**_ID_TYPE},
                "sharing_include": {
                    "type": "string",
                    "description": "Set to 'workspaceShares' to include inherited workspace shares.",
                },
            },
            required=["scope", "resource_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_get_share",
        "Get a single share on a resource.",
        _schema(
            {
                "scope": {"type": "string", "enum": ["sheets", "reports", "workspaces", "sights"]},
                "resource_id": {**_ID_TYPE},
                "share_id": {"type": "string"},
            },
            required=["scope", "resource_id", "share_id"],
        ),
    ),
    # -------------------- Automation --------------------
    _tool(
        "smartsheet_list_automation_rules",
        "List automation rules on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_automation_rule",
        "Get a single automation rule.",
        _schema(
            {**_SHEET_ID_ARG, "rule_id": {**_ID_TYPE}},
            required=["sheet_id", "rule_id"],
        ),
    ),
    # -------------------- Cross-sheet references --------------------
    _tool(
        "smartsheet_list_cross_sheet_references",
        "List cross-sheet references on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_cross_sheet_reference",
        "Get a single cross-sheet reference.",
        _schema(
            {**_SHEET_ID_ARG, "reference_id": {**_ID_TYPE}},
            required=["sheet_id", "reference_id"],
        ),
    ),
    # -------------------- Update requests --------------------
    _tool(
        "smartsheet_list_update_requests",
        "List pending update requests on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_update_request",
        "Get a single update request.",
        _schema(
            {**_SHEET_ID_ARG, "update_request_id": {**_ID_TYPE}},
            required=["sheet_id", "update_request_id"],
        ),
    ),
    _tool(
        "smartsheet_list_sent_update_requests",
        "List already-sent update requests on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_sent_update_request",
        "Get a single sent update request.",
        _schema(
            {**_SHEET_ID_ARG, "sent_update_request_id": {**_ID_TYPE}},
            required=["sheet_id", "sent_update_request_id"],
        ),
    ),
    # -------------------- Webhooks --------------------
    _tool(
        "smartsheet_list_webhooks",
        "List webhooks registered by the authenticated token.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_get_webhook",
        "Get a single webhook.",
        _schema({"webhook_id": {**_ID_TYPE}}, required=["webhook_id"]),
    ),
    # -------------------- Proofs --------------------
    _tool(
        "smartsheet_list_proofs",
        "List proofs on a sheet.",
        _schema({**_SHEET_ID_ARG}, required=["sheet_id"], pagination=True),
    ),
    _tool(
        "smartsheet_get_proof",
        "Get a single proof.",
        _schema(
            {**_SHEET_ID_ARG, "proof_id": {**_ID_TYPE}},
            required=["sheet_id", "proof_id"],
        ),
    ),
    _tool(
        "smartsheet_list_proof_attachments",
        "List attachments on a proof.",
        _schema(
            {**_SHEET_ID_ARG, "proof_id": {**_ID_TYPE}},
            required=["sheet_id", "proof_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_list_proof_discussions",
        "List discussions on a proof.",
        _schema(
            {**_SHEET_ID_ARG, "proof_id": {**_ID_TYPE}},
            required=["sheet_id", "proof_id"],
            pagination=True,
        ),
    ),
    _tool(
        "smartsheet_list_proof_request_actions",
        "List proof request action history.",
        _schema(
            {**_SHEET_ID_ARG, "proof_id": {**_ID_TYPE}},
            required=["sheet_id", "proof_id"],
            pagination=True,
        ),
    ),
    # -------------------- Templates & Favorites --------------------
    _tool(
        "smartsheet_list_templates",
        "List the user's custom templates.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_list_public_templates",
        "List Solution Center public templates.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_list_favorites",
        "List the user's favorite items.",
        _schema(pagination=True),
    ),
    _tool(
        "smartsheet_get_favorite",
        "Check whether a specific item is favorited.",
        _schema(
            {
                "favorite_type": {
                    "type": "string",
                    "enum": ["sheet", "folder", "report", "workspace", "template", "dashboard"],
                },
                "favorite_id": {**_ID_TYPE},
            },
            required=["favorite_type", "favorite_id"],
        ),
    ),
]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
HANDLERS: dict[str, Handler] = {
    # Meta
    "smartsheet_server_info": meta.server_info,
    "smartsheet_get_user_me": meta.get_user_me,
    # Sheets / columns / rows
    "smartsheet_list_sheets": sheets.list_sheets,
    "smartsheet_get_sheet": sheets.get_sheet,
    "smartsheet_list_columns": sheets.list_columns,
    "smartsheet_get_row": sheets.get_row,
    "smartsheet_get_sheet_version": structure.get_sheet_version,
    "smartsheet_get_sheet_publish": structure.get_sheet_publish,
    # Cells
    "smartsheet_get_cell_history": cells.get_cell_history,
    # Sheet summary
    "smartsheet_get_sheet_summary": summary.get_sheet_summary,
    "smartsheet_list_summary_fields": summary.list_summary_fields,
    # Search
    "smartsheet_search": search.search,
    "smartsheet_search_in_sheet": structure.search_in_sheet,
    # Workspaces
    "smartsheet_list_workspaces": workspaces.list_workspaces,
    "smartsheet_get_workspace": workspaces.get_workspace,
    "smartsheet_get_workspace_metadata": structure.get_workspace_metadata,
    "smartsheet_list_workspace_children": structure.list_workspace_children,
    # Folders
    "smartsheet_list_personal_folders": folders.list_personal_folders,
    "smartsheet_get_folder": folders.get_folder,
    "smartsheet_get_folder_metadata": structure.get_folder_metadata,
    "smartsheet_list_folder_children": structure.list_folder_children,
    # Reports
    "smartsheet_list_reports": reports.list_reports,
    "smartsheet_get_report": reports.get_report,
    "smartsheet_get_report_publish": reports.get_report_publish,
    # Dashboards
    "smartsheet_list_dashboards": dashboards.list_dashboards,
    "smartsheet_get_dashboard": dashboards.get_dashboard,
    "smartsheet_get_dashboard_publish": dashboards.get_dashboard_publish,
    # Discussions / comments
    "smartsheet_list_sheet_discussions": discussions.list_sheet_discussions,
    "smartsheet_get_discussion": discussions.get_discussion,
    "smartsheet_list_row_discussions": discussions.list_row_discussions,
    "smartsheet_list_discussion_attachments": discussions.list_discussion_attachments,
    "smartsheet_get_comment": discussions.get_comment,
    # Attachments
    "smartsheet_list_sheet_attachments": attachments.list_sheet_attachments,
    "smartsheet_list_row_attachments": attachments.list_row_attachments,
    "smartsheet_list_comment_attachments": attachments.list_comment_attachments,
    "smartsheet_get_attachment": attachments.get_attachment,
    "smartsheet_list_attachment_versions": attachments.list_attachment_versions,
    # Users / groups / contacts / alt emails
    "smartsheet_list_users": users.list_users,
    "smartsheet_get_user": users.get_user,
    "smartsheet_list_groups": users.list_groups,
    "smartsheet_get_group": users.get_group,
    "smartsheet_list_contacts": users.list_contacts,
    "smartsheet_get_contact": users.get_contact,
    "smartsheet_list_alternate_emails": users.list_alternate_emails,
    "smartsheet_get_alternate_email": users.get_alternate_email,
    # Sharing
    "smartsheet_list_shares": sharing.list_shares,
    "smartsheet_get_share": sharing.get_share,
    # Automation
    "smartsheet_list_automation_rules": automation.list_automation_rules,
    "smartsheet_get_automation_rule": automation.get_automation_rule,
    # Cross-sheet refs
    "smartsheet_list_cross_sheet_references": cross_sheet.list_cross_sheet_references,
    "smartsheet_get_cross_sheet_reference": cross_sheet.get_cross_sheet_reference,
    # Update requests
    "smartsheet_list_update_requests": update_requests.list_update_requests,
    "smartsheet_get_update_request": update_requests.get_update_request,
    "smartsheet_list_sent_update_requests": update_requests.list_sent_update_requests,
    "smartsheet_get_sent_update_request": update_requests.get_sent_update_request,
    # Webhooks
    "smartsheet_list_webhooks": webhooks.list_webhooks,
    "smartsheet_get_webhook": webhooks.get_webhook,
    # Proofs
    "smartsheet_list_proofs": proofs.list_proofs,
    "smartsheet_get_proof": proofs.get_proof,
    "smartsheet_list_proof_attachments": proofs.list_proof_attachments,
    "smartsheet_list_proof_discussions": proofs.list_proof_discussions,
    "smartsheet_list_proof_request_actions": proofs.list_proof_request_actions,
    # Templates & favorites
    "smartsheet_list_templates": extras.list_templates,
    "smartsheet_list_public_templates": extras.list_public_templates,
    "smartsheet_list_favorites": extras.list_favorites,
    "smartsheet_get_favorite": extras.get_favorite,
}


async def dispatch(
    client: SmartsheetClient,
    name: str,
    arguments: dict[str, Any] | None,
) -> Any:
    """Resolve and invoke a tool by name."""
    handler = HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(client, arguments or {})


__all__ = ["TOOLS", "HANDLERS", "dispatch"]
