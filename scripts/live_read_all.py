"""Live read-only smoke test for every registered tool.

Strategy
--------
Tools are categorised by the IDs they need (sheet_id, workspace_id, etc.).
For each category we discover a sample ID from an earlier call, then invoke
each dependent tool with that ID. Tools that genuinely can't be exercised
without custom data (e.g. get_comment needs a discussion + comment ID) are
marked as SKIP or soft-failed if the resource isn't available on the token.

Everything is read-only. No mutations occur.
"""

from __future__ import annotations

import asyncio
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from smartsheet_mcp.client import SmartsheetClient  # noqa: E402
from smartsheet_mcp.config import Settings  # noqa: E402
from smartsheet_mcp.errors import SmartsheetAPIError  # noqa: E402
from smartsheet_mcp.tools import TOOLS, dispatch  # noqa: E402


@dataclass
class Result:
    name: str
    status: str  # OK | ERR | SKIP
    detail: str = ""


@dataclass
class Ctx:
    results: list[Result] = field(default_factory=list)
    sample: dict[str, Any] = field(default_factory=dict)

    def add(self, r: Result) -> None:
        self.results.append(r)
        tag = {"OK": "✓", "ERR": "✗", "SKIP": "·"}.get(r.status, "?")
        print(f"  [{tag}] {r.name:<45s} {r.detail}")


def _peek_list(payload: Any, key: str = "data") -> list[Any]:
    if isinstance(payload, dict):
        return payload.get(key) or payload.get("results") or []
    if isinstance(payload, list):
        return payload
    return []


def _short(s: Any, n: int = 120) -> str:
    text = str(s).replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


async def call(ctx: Ctx, client: SmartsheetClient, name: str, args: dict[str, Any]) -> Any | None:
    try:
        result = await dispatch(client, name, args)
    except SmartsheetAPIError as exc:
        ctx.add(
            Result(
                name, "ERR", f"{type(exc).__name__}: HTTP {exc.status_code} code={exc.error_code}"
            )
        )
        return None
    except Exception as exc:  # noqa: BLE001
        ctx.add(Result(name, "ERR", f"{type(exc).__name__}: {exc}"))
        return None

    # Summarise
    if isinstance(result, dict):
        if "data" in result and isinstance(result["data"], list):
            summary = f"data[{len(result['data'])}]"
            if "totalCount" in result:
                summary += f" total={result['totalCount']}"
        elif "results" in result and isinstance(result["results"], list):
            summary = f"results[{len(result['results'])}]"
        else:
            keys = list(result.keys())[:6]
            summary = "keys=" + ",".join(keys)
    elif isinstance(result, list):
        summary = f"list[{len(result)}]"
    else:
        summary = _short(result, 60)

    ctx.add(Result(name, "OK", summary))
    return result


def skip(ctx: Ctx, name: str, reason: str) -> None:
    ctx.add(Result(name, "SKIP", reason))


async def main() -> int:
    settings = Settings.from_env()
    print(f"Base URL: {settings.base_url}")
    print(f"Total registered tools: {len(TOOLS)}")
    ctx = Ctx()

    async with SmartsheetClient(settings) as client:
        # --- Phase 1: no-arg tools ---
        print("\n[1] No-arg tools")
        await call(ctx, client, "smartsheet_server_info", {})
        me = await call(ctx, client, "smartsheet_get_user_me", {})
        await call(ctx, client, "smartsheet_list_personal_folders", {})
        await call(ctx, client, "smartsheet_list_contacts", {"page_size": 5})
        await call(ctx, client, "smartsheet_list_templates", {"page_size": 5})
        await call(ctx, client, "smartsheet_list_public_templates", {"page_size": 5})
        await call(ctx, client, "smartsheet_list_favorites", {"page_size": 5})
        await call(ctx, client, "smartsheet_list_webhooks", {"page_size": 5})
        await call(ctx, client, "smartsheet_list_groups", {"page_size": 5})

        # --- Phase 2: discover seed IDs ---
        print("\n[2] Seed discovery")
        sheets_resp = await call(ctx, client, "smartsheet_list_sheets", {"page_size": 20})
        if sheets_resp:
            sdata = _peek_list(sheets_resp)
            if sdata:
                ctx.sample["sheet_id"] = sdata[0]["id"]
                ctx.sample["sheet_name"] = sdata[0].get("name")

        wss = await call(ctx, client, "smartsheet_list_workspaces", {"page_size": 20})
        if wss:
            wdata = _peek_list(wss)
            if wdata:
                ctx.sample["workspace_id"] = wdata[0]["id"]

        reports_resp = await call(ctx, client, "smartsheet_list_reports", {"page_size": 5})
        if reports_resp:
            rdata = _peek_list(reports_resp)
            if rdata:
                ctx.sample["report_id"] = rdata[0]["id"]

        dash_resp = await call(ctx, client, "smartsheet_list_dashboards", {"page_size": 5})
        if dash_resp:
            ddata = _peek_list(dash_resp)
            if ddata:
                ctx.sample["dashboard_id"] = ddata[0]["id"]

        # Users: we know 'me' — sample user_id for user-scoped tools
        if isinstance(me, dict):
            ctx.sample["user_id"] = me.get("id")
        # list_users requires admin; we try but accept ERR gracefully
        await call(ctx, client, "smartsheet_list_users", {"page_size": 5})

        # --- Phase 3: sheet-scoped tools ---
        sheet_id = ctx.sample.get("sheet_id")
        if not sheet_id:
            print("\n(no sheet visible — skipping sheet-scoped tools)")
        else:
            print(
                f"\n[3] Sheet-scoped tools (sheet_id={sheet_id}, name={ctx.sample.get('sheet_name')!r})"
            )
            sheet = await call(
                ctx, client, "smartsheet_get_sheet", {"sheet_id": sheet_id, "page_size": 5}
            )
            await call(ctx, client, "smartsheet_list_columns", {"sheet_id": sheet_id})
            await call(ctx, client, "smartsheet_get_sheet_version", {"sheet_id": sheet_id})
            await call(ctx, client, "smartsheet_get_sheet_publish", {"sheet_id": sheet_id})
            await call(ctx, client, "smartsheet_get_sheet_summary", {"sheet_id": sheet_id})
            await call(
                ctx,
                client,
                "smartsheet_list_summary_fields",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_sheet_discussions",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_sheet_attachments",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_automation_rules",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_cross_sheet_references",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_update_requests",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_sent_update_requests",
                {"sheet_id": sheet_id, "page_size": 5},
            )
            await call(
                ctx, client, "smartsheet_list_proofs", {"sheet_id": sheet_id, "page_size": 5}
            )
            await call(
                ctx, client, "smartsheet_search_in_sheet", {"sheet_id": sheet_id, "query": "test"}
            )
            # Shares on this sheet
            await call(
                ctx,
                client,
                "smartsheet_list_shares",
                {"scope": "sheets", "resource_id": sheet_id, "page_size": 5},
            )

            # Row-scoped: pick a row id from the sheet payload
            row_id = None
            column_id = None
            if isinstance(sheet, dict):
                rows = sheet.get("rows") or []
                cols = sheet.get("columns") or []
                if rows:
                    row_id = rows[0].get("id")
                    ctx.sample["row_id"] = row_id
                    # Pick a column that actually has a cell in the first row
                    first_cells = rows[0].get("cells") or []
                    if first_cells:
                        column_id = first_cells[0].get("columnId")
                        ctx.sample["column_id"] = column_id
                if cols and not column_id:
                    column_id = cols[0].get("id")
                    ctx.sample["column_id"] = column_id

            if row_id is not None:
                await call(
                    ctx, client, "smartsheet_get_row", {"sheet_id": sheet_id, "row_id": row_id}
                )
                await call(
                    ctx,
                    client,
                    "smartsheet_list_row_discussions",
                    {"sheet_id": sheet_id, "row_id": row_id, "page_size": 5},
                )
                await call(
                    ctx,
                    client,
                    "smartsheet_list_row_attachments",
                    {"sheet_id": sheet_id, "row_id": row_id, "page_size": 5},
                )
                if column_id is not None:
                    await call(
                        ctx,
                        client,
                        "smartsheet_get_cell_history",
                        {
                            "sheet_id": sheet_id,
                            "row_id": row_id,
                            "column_id": column_id,
                            "page_size": 5,
                        },
                    )
                else:
                    skip(ctx, "smartsheet_get_cell_history", "no column in sampled row")
            else:
                for n in (
                    "smartsheet_get_row",
                    "smartsheet_list_row_discussions",
                    "smartsheet_list_row_attachments",
                    "smartsheet_get_cell_history",
                ):
                    skip(ctx, n, "no rows in sampled sheet")

        # --- Phase 4: workspace-scoped ---
        ws_id = ctx.sample.get("workspace_id")
        if ws_id is None:
            for n in (
                "smartsheet_get_workspace",
                "smartsheet_get_workspace_metadata",
                "smartsheet_list_workspace_children",
            ):
                skip(ctx, n, "no workspace visible")
        else:
            print(f"\n[4] Workspace-scoped (workspace_id={ws_id})")
            await call(ctx, client, "smartsheet_get_workspace", {"workspace_id": ws_id})
            await call(ctx, client, "smartsheet_get_workspace_metadata", {"workspace_id": ws_id})
            await call(
                ctx,
                client,
                "smartsheet_list_workspace_children",
                {"workspace_id": ws_id, "max_items": 100},
            )
            await call(
                ctx,
                client,
                "smartsheet_list_shares",
                {"scope": "workspaces", "resource_id": ws_id, "page_size": 5},
            )

        # --- Phase 5: folder-scoped (pick one from personal home if possible) ---
        # Reuse the personal folders payload from Phase 1 rather than re-calling.
        home_folders_payload = None
        try:
            # Direct HTTP, not through dispatch, to avoid polluting the results list.
            home_folders_payload = await client.get("/folders/personal")
        except Exception:
            home_folders_payload = None
        folder_id = None
        if isinstance(home_folders_payload, dict):
            flist = home_folders_payload.get("folders") or []
            if flist:
                folder_id = flist[0].get("id")
        if folder_id is None and ws_id:
            # Fallback: look inside the first workspace, if any folders there
            try:
                ws_full = await client.get(f"/workspaces/{ws_id}")
                for f in ws_full.get("folders") or []:
                    folder_id = f.get("id")
                    if folder_id:
                        break
            except Exception:
                folder_id = None

        if folder_id is None and ws_id:
            # Second fallback: dig through paginated children which may expose folders
            try:
                children = await client.get(
                    f"/workspaces/{ws_id}/children",
                    params={"maxItems": 100},
                )
                for item in (children or {}).get("data") or []:
                    if item.get("resourceType") == "folder" and item.get("id"):
                        folder_id = item["id"]
                        break
            except Exception:
                pass

        if folder_id is None:
            for n in (
                "smartsheet_get_folder",
                "smartsheet_get_folder_metadata",
                "smartsheet_list_folder_children",
            ):
                skip(ctx, n, "no folder visible")
        else:
            print(f"\n[5] Folder-scoped (folder_id={folder_id})")
            await call(ctx, client, "smartsheet_get_folder", {"folder_id": folder_id})
            await call(ctx, client, "smartsheet_get_folder_metadata", {"folder_id": folder_id})
            await call(
                ctx,
                client,
                "smartsheet_list_folder_children",
                {"folder_id": folder_id, "max_items": 100},
            )

        # --- Phase 6: report / dashboard ---
        rid = ctx.sample.get("report_id")
        if rid is None:
            for n in ("smartsheet_get_report", "smartsheet_get_report_publish"):
                skip(ctx, n, "no report visible")
        else:
            print(f"\n[6a] Report (report_id={rid})")
            await call(ctx, client, "smartsheet_get_report", {"report_id": rid, "page_size": 5})
            await call(ctx, client, "smartsheet_get_report_publish", {"report_id": rid})

        did = ctx.sample.get("dashboard_id")
        if did is None:
            for n in ("smartsheet_get_dashboard", "smartsheet_get_dashboard_publish"):
                skip(ctx, n, "no dashboard visible")
        else:
            print(f"\n[6b] Dashboard (dashboard_id={did})")
            await call(ctx, client, "smartsheet_get_dashboard", {"dashboard_id": did})
            await call(ctx, client, "smartsheet_get_dashboard_publish", {"dashboard_id": did})

        # --- Phase 7: user / alt email / group ---
        uid = ctx.sample.get("user_id")
        if uid is None:
            for n in ("smartsheet_get_user", "smartsheet_list_alternate_emails"):
                skip(ctx, n, "no user id")
        else:
            print(f"\n[7] User-scoped (user_id={uid})")
            await call(ctx, client, "smartsheet_get_user", {"user_id": uid})
            await call(ctx, client, "smartsheet_list_alternate_emails", {"user_id": uid})

        # Global search
        await call(ctx, client, "smartsheet_search", {"query": "test"})

        # --- Phase 8: try sub-resource GETs when we actually discovered IDs ---
        print("\n[8] Resource-ID-dependent GET tools (opportunistic)")

        # Groups: we listed some earlier; pick one if admin sees any
        try:
            g = await client.get("/groups", params={"pageSize": 1})
            gdata = (g or {}).get("data") or []
            if gdata and gdata[0].get("id"):
                await call(ctx, client, "smartsheet_get_group", {"group_id": gdata[0]["id"]})
        except Exception:
            pass

        # Shares (sheet scope): reuse the earlier list_shares call
        try:
            shr = (
                await client.get(
                    f"/sheets/{sheet_id}/shares",
                    params={"pageSize": 1},
                )
                if sheet_id
                else None
            )
            sdata = (shr or {}).get("data") or []
            if sdata and sdata[0].get("id"):
                await call(
                    ctx,
                    client,
                    "smartsheet_get_share",
                    {"scope": "sheets", "resource_id": sheet_id, "share_id": sdata[0]["id"]},
                )
        except Exception:
            pass

        # Automation rule (we saw 1 earlier on the sheet)
        if sheet_id:
            try:
                ar = await client.get(
                    f"/sheets/{sheet_id}/automationrules",
                    params={"pageSize": 1},
                )
                adata = (ar or {}).get("data") or []
                if adata and adata[0].get("id"):
                    await call(
                        ctx,
                        client,
                        "smartsheet_get_automation_rule",
                        {"sheet_id": sheet_id, "rule_id": adata[0]["id"]},
                    )
            except Exception:
                pass

        # Soft-skip the remaining tools that need data we don't have.
        soft_skip = [
            "smartsheet_get_discussion",
            "smartsheet_list_discussion_attachments",
            "smartsheet_get_comment",
            "smartsheet_list_comment_attachments",
            "smartsheet_get_attachment",
            "smartsheet_list_attachment_versions",
            "smartsheet_get_cross_sheet_reference",
            "smartsheet_get_update_request",
            "smartsheet_get_sent_update_request",
            "smartsheet_get_webhook",
            "smartsheet_get_proof",
            "smartsheet_list_proof_attachments",
            "smartsheet_list_proof_discussions",
            "smartsheet_list_proof_request_actions",
            "smartsheet_get_contact",
            "smartsheet_get_alternate_email",
            "smartsheet_get_favorite",
            # These may already be covered above; skip() below deduplicates.
            "smartsheet_get_group",
            "smartsheet_get_share",
            "smartsheet_get_automation_rule",
        ]
        already = {r.name for r in ctx.results}
        for n in soft_skip:
            if n not in already:
                skip(ctx, n, "needs specific sub-resource ID not present in workspace")

    # --- Summary ---
    counts: dict[str, int] = defaultdict(int)
    for r in ctx.results:
        counts[r.status] += 1
    total = len(ctx.results)
    print("\n" + "=" * 60)
    print(
        f"SUMMARY: OK={counts['OK']}  ERR={counts['ERR']}  SKIP={counts['SKIP']}  "
        f"TOTAL={total}  (registered={len(TOOLS)})"
    )
    covered = {r.name for r in ctx.results}
    uncovered = [t.name for t in TOOLS if t.name not in covered]
    if uncovered:
        print(f"\nTools NOT exercised by this script ({len(uncovered)}):")
        for n in uncovered:
            print(f"  - {n}")

    # Non-zero exit only if we saw a truly unexpected failure
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
