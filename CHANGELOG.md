# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-02

### Added
- Initial read-only release: **66 tools** covering the Smartsheet REST API.
- Meta: `smartsheet_server_info`, `smartsheet_get_user_me`.
- Sheets / columns / rows / cells: `list_sheets`, `get_sheet`, `list_columns`,
  `get_row`, `get_sheet_version`, `get_sheet_publish`, `get_cell_history`.
- Sheet summary: `get_sheet_summary`, `list_summary_fields`.
- Workspaces / folders (including paginated `*_children`, `*_metadata`).
- Reports, dashboards (sights), discussions, comments, attachments,
  automation rules, cross-sheet references, update requests (pending + sent),
  webhooks, proofs, templates, favorites, users, groups, contacts,
  alternate emails, and sharing (sheets/reports/workspaces/sights).
- Two optional verification scripts under `scripts/`: `live_read_all.py`,
  `show_sheet_sample.py`.
- Strict environment-variable configuration (`SMARTSHEET_ACCESS_TOKEN`,
  `SMARTSHEET_API_BASE_URL`, `SMARTSHEET_TIMEOUT`, `SMARTSHEET_LOG_LEVEL`).
- Stdio MCP transport via the official `mcp` Python SDK.

### Intentionally excluded
- All write operations (add/update/delete rows, cell updates, sheet/column
  mutations, webhook registration, etc.).
- `list_events` — the Smartsheet Events API requires an Enterprise premium
  add-on; the endpoint is not exposed here until it can be exercised under a
  supported plan.
