"""Shared helpers for tool handlers."""

from __future__ import annotations

from typing import Any


def csv(values: list[Any] | None) -> str | None:
    """Join a list of values into a comma-separated string for query params."""
    if not values:
        return None
    return ",".join(str(v) for v in values)


def pagination_params(args: dict[str, Any]) -> dict[str, Any]:
    """Extract common Smartsheet pagination query params from tool arguments."""
    params: dict[str, Any] = {
        "page": args.get("page"),
        "pageSize": args.get("page_size"),
    }
    if args.get("include_all"):
        params["includeAll"] = "true"
    return params
