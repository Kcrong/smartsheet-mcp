"""Async HTTP client for the Smartsheet REST API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import Settings
from .errors import (
    SmartsheetAPIError,
    SmartsheetAuthError,
    SmartsheetNotFoundError,
    SmartsheetRateLimitError,
)

logger = logging.getLogger(__name__)

USER_AGENT = "smartsheet-mcp/0.1.0 (+https://github.com/Kcrong/smartsheet-mcp)"


class SmartsheetClient:
    """Thin async wrapper around the Smartsheet 2.0 REST API.

    Only exposes primitives the MCP tools need: authenticated GET with
    structured error handling. Designed for the read-only MVP.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=settings.timeout,
            headers={
                "Authorization": f"Bearer {settings.access_token}",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> SmartsheetClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # ------------------------------------------------------------------
    # Low-level request
    # ------------------------------------------------------------------
    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Perform an authenticated GET and return parsed JSON.

        Raises a typed subclass of :class:`SmartsheetAPIError` on non-2xx.
        """
        clean_params = _clean_params(params)
        logger.debug("GET %s params=%s", path, clean_params)

        try:
            response = await self._http.get(path, params=clean_params)
        except httpx.TimeoutException as exc:
            raise SmartsheetAPIError(
                status_code=0,
                message=f"Request to {path} timed out: {exc}",
            ) from exc
        except httpx.HTTPError as exc:
            raise SmartsheetAPIError(
                status_code=0,
                message=f"HTTP error on {path}: {exc}",
            ) from exc

        return _handle_response(response)


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values so httpx does not send empty query keys."""
    if not params:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _handle_response(response: httpx.Response) -> Any:
    if response.is_success:
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise SmartsheetAPIError(
                status_code=response.status_code,
                message=f"Response was not valid JSON: {exc}",
            ) from exc

    # Error path — try to extract structured Smartsheet error payload.
    error_code: int | None = None
    ref_id: str | None = None
    message = response.reason_phrase or "Unknown error"
    detail: Any = None

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        message = payload.get("message") or message
        error_code = payload.get("errorCode")
        ref_id = payload.get("refId")
        detail = payload.get("detail")

    status = response.status_code
    exc_cls: type[SmartsheetAPIError]
    if status in (401, 403):
        exc_cls = SmartsheetAuthError
    elif status == 404:
        exc_cls = SmartsheetNotFoundError
    elif status == 429:
        exc_cls = SmartsheetRateLimitError
    else:
        exc_cls = SmartsheetAPIError

    raise exc_cls(
        status_code=status,
        message=message,
        error_code=error_code,
        ref_id=ref_id,
        detail=detail,
    )
