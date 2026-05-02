# smartsheet-mcp

[![CI](https://github.com/Kcrong/smartsheet-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Kcrong/smartsheet-mcp/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/smartsheet-mcp.svg)](https://pypi.org/project/smartsheet-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/smartsheet-mcp.svg)](https://pypi.org/project/smartsheet-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes
[Smartsheet](https://www.smartsheet.com/) **read APIs** as MCP tools, so you
can browse and query Smartsheet data from any MCP-compatible client (for
example, Kiro).

> **Status:** read-only, 66 tools covering the Smartsheet read surface.
> Write operations (add/update/delete rows, create sheets, register webhooks,
> etc.) are **not** implemented — this server is intentionally safe for
> exploration and reporting workflows.

---

## Quick start

1. **Get a Smartsheet API access token** — see
   [Getting an API key](#getting-an-api-key).
2. **Install the server** — see [Install](#install).
3. **Configure it** — export `SMARTSHEET_ACCESS_TOKEN` or put it in a `.env`
   file.
4. **Register with your MCP client** — see [Register with Kiro](#register-with-kiro).

---

## Getting an API key

The Smartsheet API uses a bearer access token.

> **Requirement**: your Smartsheet account must be on a **Business or
> Enterprise plan**. Free / Pro plans cannot access the public API.

1. Sign in to [Smartsheet](https://app.smartsheet.com).
2. In the bottom-left corner, click **Account** → **Personal Settings**.
3. Open the **API Access** tab.
4. Click **Generate new access token**, give it a descriptive name, and
   confirm.
5. **Copy the token immediately** — Smartsheet will only show it to you once.
6. Store it somewhere safe (a password manager or secret store). You will
   paste it into an environment variable or `.env` file, **not** into source
   control.

Smartsheet's own walkthrough, with screenshots:
<https://help.smartsheet.com/articles/2482389-generate-API-key>.

### Regional endpoints

If your Smartsheet account lives outside the US, override the base URL:

| Region | Base URL |
|--------|----------|
| US (default) | `https://api.smartsheet.com/2.0` |
| EU | `https://api.smartsheet.eu/2.0` |
| Australia | `https://api.smartsheet.au/2.0` |

Set it with `SMARTSHEET_API_BASE_URL`.

### Rotating or revoking a token

If a token is leaked (committed to git, pasted in a chat, etc.) revoke it
immediately:

1. Return to **Account → Personal Settings → API Access**.
2. Click the **⋯** menu next to the token and choose **Revoke**.
3. Generate a new one and update every place that uses it.

---

## Install

**Requires Python 3.10+.**

### Option 1 — install from PyPI (recommended for end users)

```bash
pip install smartsheet-mcp
```

Or with [`pipx`](https://pipx.pypa.io/) to keep it isolated:

```bash
pipx install smartsheet-mcp
```

Either way, the `smartsheet-mcp` command is now on your `PATH`.

### Option 2 — editable install from source (for contributors)

```bash
git clone https://github.com/Kcrong/smartsheet-mcp.git
cd smartsheet-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 3 — with [`uv`](https://docs.astral.sh/uv/)

```bash
# Run without installing, one-off
uvx smartsheet-mcp --version

# Or develop from source
git clone https://github.com/Kcrong/smartsheet-mcp.git
cd smartsheet-mcp
uv venv
source .venv/bin/activate
uv pip install -e .
```

After install, `smartsheet-mcp` is on your `PATH` and
`python -m smartsheet_mcp` works too.

---

## Configure

The server reads all configuration from environment variables.

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `SMARTSHEET_ACCESS_TOKEN` | ✅ | — | Bearer token from the steps above |
| `SMARTSHEET_API_BASE_URL` | ❌ | `https://api.smartsheet.com/2.0` | Override for EU/AU regions |
| `SMARTSHEET_TIMEOUT` | ❌ | `30` | HTTP timeout in seconds |
| `SMARTSHEET_LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### Option A — environment variable

```bash
export SMARTSHEET_ACCESS_TOKEN="paste-your-token-here"
smartsheet-mcp
```

### Option B — `.env` file (good for local development)

Copy the template and fill it in:

```bash
cp .env.example .env
# edit .env and set SMARTSHEET_ACCESS_TOKEN
```

`.env` is already listed in `.gitignore`.

### Smoke test

```bash
smartsheet-mcp --help
smartsheet-mcp --version

# Start the server (stdio; it will wait for MCP messages from a client)
SMARTSHEET_ACCESS_TOKEN=... smartsheet-mcp
# Ctrl+C to stop.
```

An end-to-end check against a real token:

```bash
# Print a few sample rows from one accessible sheet
SMARTSHEET_ACCESS_TOKEN=... python scripts/show_sheet_sample.py

# Call every registered tool (read-only)
SMARTSHEET_ACCESS_TOKEN=... python scripts/live_read_all.py
```

---

## Register with Kiro

Kiro reads MCP server configuration from either:

- Project-local: `.kiro/settings/mcp.json` (checked into your project, but
  **this file is gitignored in this repo** to avoid leaking tokens), or
- Global: `~/.kiro/settings/mcp.json` (recommended for personal tokens).

This repo ships `.kiro/settings/mcp.example.json` as a starting point. Copy
it and fill in the real values:

```bash
cp .kiro/settings/mcp.example.json .kiro/settings/mcp.json
# edit .kiro/settings/mcp.json
```

Minimal example entry (point `command` at the interpreter inside your venv):

```json
{
  "mcpServers": {
    "smartsheet": {
      "command": "/absolute/path/to/smartsheet-mcp/.venv/bin/python",
      "args": ["-m", "smartsheet_mcp"],
      "env": {
        "SMARTSHEET_ACCESS_TOKEN": "paste-your-token-here"
      },
      "timeout": 120000
    }
  }
}
```

If you installed the project so that `smartsheet-mcp` is on Kiro's `PATH`:

```json
{
  "mcpServers": {
    "smartsheet": {
      "command": "smartsheet-mcp",
      "env": {
        "SMARTSHEET_ACCESS_TOKEN": "paste-your-token-here"
      },
      "timeout": 120000
    }
  }
}
```

Restart Kiro (or reload MCP servers) after editing the config. Confirm the
server is live by asking Kiro to call `smartsheet_get_user_me` or
`smartsheet_list_sheets`.

### Security notes for the config file

- **Never commit `.kiro/settings/mcp.json`.** It is already in `.gitignore`;
  keep it that way.
- Prefer Kiro's **global** config (`~/.kiro/settings/mcp.json`) for personal
  tokens so they never appear inside a project checkout.
- For shared/CI use, consider an **OAuth-issued service token** on a
  dedicated Smartsheet account rather than a developer's personal token.

---

## Available tools (66)

All tools are prefixed `smartsheet_`.

### Meta
| Tool | Endpoint |
|------|----------|
| `smartsheet_server_info` | `GET /serverinfo` |
| `smartsheet_get_user_me` | `GET /users/me` |

### Sheets, columns, rows, cells
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_sheets` | `GET /sheets` |
| `smartsheet_get_sheet` | `GET /sheets/{id}` |
| `smartsheet_list_columns` | `GET /sheets/{id}/columns` |
| `smartsheet_get_row` | `GET /sheets/{id}/rows/{rowId}` |
| `smartsheet_get_sheet_version` | `GET /sheets/{id}/version` |
| `smartsheet_get_sheet_publish` | `GET /sheets/{id}/publish` |
| `smartsheet_get_cell_history` | `GET /sheets/{id}/rows/{rowId}/columns/{colId}/history` |

### Sheet summary
| Tool | Endpoint |
|------|----------|
| `smartsheet_get_sheet_summary` | `GET /sheets/{id}/summary` |
| `smartsheet_list_summary_fields` | `GET /sheets/{id}/summary/fields` |

### Search
| Tool | Endpoint |
|------|----------|
| `smartsheet_search` | `GET /search` |
| `smartsheet_search_in_sheet` | `GET /search/sheets/{id}` |

### Workspaces
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_workspaces` | `GET /workspaces` |
| `smartsheet_get_workspace` | `GET /workspaces/{id}` |
| `smartsheet_get_workspace_metadata` | `GET /workspaces/{id}/metadata` |
| `smartsheet_list_workspace_children` | `GET /workspaces/{id}/children` (token-paginated) |

### Folders
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_personal_folders` | `GET /folders/personal` |
| `smartsheet_get_folder` | `GET /folders/{id}` |
| `smartsheet_get_folder_metadata` | `GET /folders/{id}/metadata` |
| `smartsheet_list_folder_children` | `GET /folders/{id}/children` (token-paginated) |

### Reports
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_reports` | `GET /reports` |
| `smartsheet_get_report` | `GET /reports/{id}` |
| `smartsheet_get_report_publish` | `GET /reports/{id}/publish` |

### Dashboards (Sights)
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_dashboards` | `GET /sights` |
| `smartsheet_get_dashboard` | `GET /sights/{id}` |
| `smartsheet_get_dashboard_publish` | `GET /sights/{id}/publish` |

### Discussions & comments
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_sheet_discussions` | `GET /sheets/{id}/discussions` |
| `smartsheet_get_discussion` | `GET /sheets/{id}/discussions/{id}` |
| `smartsheet_list_row_discussions` | `GET /sheets/{id}/rows/{rowId}/discussions` |
| `smartsheet_list_discussion_attachments` | `GET /sheets/{id}/discussions/{id}/attachments` |
| `smartsheet_get_comment` | `GET /sheets/{id}/comments/{id}` |

### Attachments
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_sheet_attachments` | `GET /sheets/{id}/attachments` |
| `smartsheet_list_row_attachments` | `GET /sheets/{id}/rows/{rowId}/attachments` |
| `smartsheet_list_comment_attachments` | `GET /sheets/{id}/comments/{id}/attachments` |
| `smartsheet_get_attachment` | `GET /sheets/{id}/attachments/{id}` |
| `smartsheet_list_attachment_versions` | `GET /sheets/{id}/attachments/{id}/versions` |

### Users, groups, contacts, alternate emails
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_users` | `GET /users` |
| `smartsheet_get_user` | `GET /users/{id}` |
| `smartsheet_list_groups` | `GET /groups` |
| `smartsheet_get_group` | `GET /groups/{id}` |
| `smartsheet_list_contacts` | `GET /contacts` |
| `smartsheet_get_contact` | `GET /contacts/{id}` |
| `smartsheet_list_alternate_emails` | `GET /users/{id}/alternateemails` |
| `smartsheet_get_alternate_email` | `GET /users/{id}/alternateemails/{altId}` |

### Sharing
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_shares` | `GET /{scope}/{id}/shares` (`sheets`, `reports`, `workspaces`, `sights`) |
| `smartsheet_get_share` | `GET /{scope}/{id}/shares/{shareId}` |

### Automation & cross-sheet references
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_automation_rules` | `GET /sheets/{id}/automationrules` |
| `smartsheet_get_automation_rule` | `GET /sheets/{id}/automationrules/{id}` |
| `smartsheet_list_cross_sheet_references` | `GET /sheets/{id}/crosssheetreferences` |
| `smartsheet_get_cross_sheet_reference` | `GET /sheets/{id}/crosssheetreferences/{id}` |

### Update requests
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_update_requests` | `GET /sheets/{id}/updaterequests` |
| `smartsheet_get_update_request` | `GET /sheets/{id}/updaterequests/{id}` |
| `smartsheet_list_sent_update_requests` | `GET /sheets/{id}/sentupdaterequests` |
| `smartsheet_get_sent_update_request` | `GET /sheets/{id}/sentupdaterequests/{id}` |

### Webhooks & proofs
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_webhooks` | `GET /webhooks` |
| `smartsheet_get_webhook` | `GET /webhooks/{id}` |
| `smartsheet_list_proofs` | `GET /sheets/{id}/proofs` |
| `smartsheet_get_proof` | `GET /sheets/{id}/proofs/{id}` |
| `smartsheet_list_proof_attachments` | `GET /sheets/{id}/proofs/{id}/attachments` |
| `smartsheet_list_proof_discussions` | `GET /sheets/{id}/proofs/{id}/discussions` |
| `smartsheet_list_proof_request_actions` | `GET /sheets/{id}/proofs/{id}/requestactions` |

### Templates & favorites
| Tool | Endpoint |
|------|----------|
| `smartsheet_list_templates` | `GET /templates` |
| `smartsheet_list_public_templates` | `GET /templates/public` |
| `smartsheet_list_favorites` | `GET /favorites` |
| `smartsheet_get_favorite` | `GET /favorites/{type}/{id}` |

---

## Project layout

```
smartsheet-mcp/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── .env.example
├── .gitignore
├── .kiro/settings/mcp.example.json    # template; the real mcp.json is gitignored
├── scripts/
│   ├── live_read_all.py               # calls every tool with a real token
│   └── show_sheet_sample.py           # prints a sample sheet as a table
└── src/smartsheet_mcp/
    ├── __init__.py
    ├── __main__.py                    # python -m smartsheet_mcp
    ├── server.py                      # MCP stdio server
    ├── client.py                      # Async Smartsheet HTTP client (httpx)
    ├── config.py                      # Env-var settings
    ├── errors.py                      # Typed exceptions
    └── tools/
        ├── __init__.py                # Tool catalog + dispatcher (66 tools)
        ├── _common.py
        ├── meta.py
        ├── sheets.py
        ├── cells.py
        ├── summary.py
        ├── search.py
        ├── workspaces.py
        ├── folders.py
        ├── structure.py               # metadata/children/version/publish/in-sheet search
        ├── reports.py
        ├── dashboards.py
        ├── discussions.py
        ├── attachments.py
        ├── users.py
        ├── sharing.py
        ├── automation.py
        ├── cross_sheet.py
        ├── update_requests.py
        ├── webhooks.py
        ├── proofs.py
        └── extras.py                  # templates, favorites
```

---

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `RuntimeError: SMARTSHEET_ACCESS_TOKEN is not set` | Export the variable or create `.env`. |
| HTTP 401 on every call | Token is invalid, revoked, or from the wrong region. Verify in the Smartsheet UI. |
| HTTP 403 errorCode 1004 | Your plan does not include this feature (e.g. Events Reporting is Enterprise-only). |
| HTTP 400 errorCode 2238 on `*_children` | `max_items` must be 100..1000 and a multiple of 100; don't use `page_size` here. |
| Kiro doesn't see the server | Check `mcp.json` path; restart Kiro; confirm `smartsheet-mcp --help` works in the same shell. |

---

## Roadmap

Write operations are deliberately out of scope for v0.x. Candidate follow-ups:

- Write tools: add/update/delete rows, update cells.
- Sheet create/copy/move/delete, column add/update/delete.
- Attachments upload/delete/download binary.
- Discussions/comments create/update/delete.
- Webhooks register/enable/delete, event callbacks.
- Automation rules / update requests create & modify.
- `list_events` once a test account with the premium add-on is available.
- Recorded API fixtures + automated pytest suite.

---

## License

[MIT](LICENSE).
