"""Proof read tools."""

from __future__ import annotations

from typing import Any

from ..client import SmartsheetClient
from ._common import pagination_params


async def list_proofs(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/proofs — all proofs on a sheet."""
    sheet_id = args["sheet_id"]
    return await client.get(f"/sheets/{sheet_id}/proofs", params=pagination_params(args))


async def get_proof(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/proofs/{proofId} — single proof."""
    sheet_id = args["sheet_id"]
    proof_id = args["proof_id"]
    return await client.get(f"/sheets/{sheet_id}/proofs/{proof_id}")


async def list_proof_attachments(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/proofs/{proofId}/attachments — attachments on a proof."""
    sheet_id = args["sheet_id"]
    proof_id = args["proof_id"]
    return await client.get(
        f"/sheets/{sheet_id}/proofs/{proof_id}/attachments",
        params=pagination_params(args),
    )


async def list_proof_discussions(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/proofs/{proofId}/discussions — discussions on a proof."""
    sheet_id = args["sheet_id"]
    proof_id = args["proof_id"]
    return await client.get(
        f"/sheets/{sheet_id}/proofs/{proof_id}/discussions",
        params=pagination_params(args),
    )


async def list_proof_request_actions(client: SmartsheetClient, args: dict[str, Any]) -> Any:
    """GET /sheets/{id}/proofs/{proofId}/requestactions — proof request history."""
    sheet_id = args["sheet_id"]
    proof_id = args["proof_id"]
    return await client.get(
        f"/sheets/{sheet_id}/proofs/{proof_id}/requestactions",
        params=pagination_params(args),
    )
