"""Custom exceptions for the Smartsheet MCP server."""

from __future__ import annotations

from typing import Any


class SmartsheetError(Exception):
    """Base exception for all Smartsheet-related errors."""


class SmartsheetAPIError(SmartsheetError):
    """Raised when the Smartsheet API returns a non-2xx response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        error_code: int | None = None,
        ref_id: str | None = None,
        detail: Any = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.ref_id = ref_id
        self.detail = detail
        super().__init__(self._format(status_code, message, error_code, ref_id))

    @staticmethod
    def _format(status: int, message: str, code: int | None, ref: str | None) -> str:
        parts = [f"HTTP {status}"]
        if code is not None:
            parts.append(f"code={code}")
        if ref:
            parts.append(f"refId={ref}")
        parts.append(message or "(no message)")
        return " | ".join(parts)


class SmartsheetAuthError(SmartsheetAPIError):
    """Raised for 401/403 authentication/authorization failures."""


class SmartsheetNotFoundError(SmartsheetAPIError):
    """Raised for 404 not found."""


class SmartsheetRateLimitError(SmartsheetAPIError):
    """Raised for 429 rate limited."""
