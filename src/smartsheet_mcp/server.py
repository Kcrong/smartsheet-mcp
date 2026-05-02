"""MCP server entry point for Smartsheet (stdio transport)."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import SmartsheetClient
from .config import Settings, configure_logging
from .errors import SmartsheetAPIError
from .tools import TOOLS, dispatch

logger = logging.getLogger("smartsheet_mcp")

SERVER_NAME = "smartsheet-mcp"
SERVER_VERSION = "0.1.0"

HELP_TEXT = (
    "smartsheet-mcp — Model Context Protocol server for Smartsheet (stdio)\n"
    "\n"
    "Usage:\n"
    "  smartsheet-mcp            # run the stdio MCP server\n"
    "  python -m smartsheet_mcp  # same thing\n"
    "\n"
    "Environment:\n"
    "  SMARTSHEET_ACCESS_TOKEN   (required) Smartsheet API access token\n"
    "  SMARTSHEET_API_BASE_URL   (optional) default: https://api.smartsheet.com/2.0\n"
    "  SMARTSHEET_TIMEOUT        (optional) request timeout seconds (default: 30)\n"
    "  SMARTSHEET_LOG_LEVEL      (optional) DEBUG|INFO|WARNING|ERROR (default: INFO)\n"
    "\n"
    "This server speaks MCP over stdio. Register it in your MCP client\n"
    "(e.g. Kiro's .kiro/settings/mcp.json). See README.md for details."
)


def _json_text(payload: Any) -> list[TextContent]:
    """Serialize any JSON-compatible payload to a single text content block."""
    try:
        text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    except (TypeError, ValueError):
        text = str(payload)
    return [TextContent(type="text", text=text)]


def _error_text(message: str) -> list[TextContent]:
    return [TextContent(type="text", text=f"Error: {message}")]


async def _run(settings: Settings) -> None:
    server: Server = Server(SERVER_NAME)
    client = SmartsheetClient(settings)

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        try:
            result = await dispatch(client, name, arguments)
        except SmartsheetAPIError as exc:
            logger.warning("Smartsheet API error on tool %s: %s", name, exc)
            return _error_text(str(exc))
        except Exception as exc:  # noqa: BLE001 — surface any failure to the caller
            logger.exception("Unhandled error on tool %s", name)
            return _error_text(f"{type(exc).__name__}: {exc}")
        return _json_text(result)

    init_options = InitializationOptions(
        server_name=SERVER_NAME,
        server_version=SERVER_VERSION,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("%s %s started (stdio)", SERVER_NAME, SERVER_VERSION)
            await server.run(read_stream, write_stream, init_options)
    finally:
        await client.aclose()


def main() -> None:
    """CLI entry point — loads config, configures logging, runs the server."""
    argv = sys.argv[1:]
    if argv and argv[0] in ("-h", "--help"):
        print(HELP_TEXT)
        return
    if argv and argv[0] in ("-V", "--version"):
        print(f"{SERVER_NAME} {SERVER_VERSION}")
        return
    if argv:
        print(f"Unknown argument: {argv[0]}\n", file=sys.stderr)
        print(HELP_TEXT, file=sys.stderr)
        sys.exit(2)

    settings = Settings.from_env()
    configure_logging(settings.log_level)
    asyncio.run(_run(settings))
