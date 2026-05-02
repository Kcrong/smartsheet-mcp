"""Configuration loader for the Smartsheet MCP server."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file if present (silently ignored if missing)
load_dotenv()

DEFAULT_BASE_URL = "https://api.smartsheet.com/2.0"
DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Smartsheet client."""

    access_token: str
    base_url: str
    timeout: float
    log_level: str

    @classmethod
    def from_env(cls) -> Settings:
        token = os.getenv("SMARTSHEET_ACCESS_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "SMARTSHEET_ACCESS_TOKEN is not set. "
                "Generate one at https://help.smartsheet.com/articles/2482389-generate-API-key "
                "and set it as an environment variable or in a .env file."
            )

        base_url = os.getenv("SMARTSHEET_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

        raw_timeout = os.getenv("SMARTSHEET_TIMEOUT")
        try:
            timeout = float(raw_timeout) if raw_timeout else DEFAULT_TIMEOUT
        except ValueError:
            timeout = DEFAULT_TIMEOUT

        log_level = os.getenv("SMARTSHEET_LOG_LEVEL", "INFO").upper()

        return cls(
            access_token=token,
            base_url=base_url,
            timeout=timeout,
            log_level=log_level,
        )


def configure_logging(level: str) -> None:
    """Configure root logger. MCP stdio uses stdout for protocol; logs go to stderr."""
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
