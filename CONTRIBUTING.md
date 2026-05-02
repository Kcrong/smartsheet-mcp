# Contributing to smartsheet-mcp

Thanks for your interest! This project is a read-only MCP server for
Smartsheet. Contributions of all kinds are welcome: bug reports, docs, and
code.

## Ground rules

- **Keep it read-only.** Adding write/mutation tools is a deliberate choice
  that requires design review. Open an issue first to discuss scope.
- **Never commit API tokens or production URLs.** See `.gitignore` — the
  local `.kiro/settings/mcp.json` and any `.env*` file are excluded on
  purpose.
- **Follow the existing patterns.** New tools should:
  1. Add a handler under `src/smartsheet_mcp/tools/<category>.py`.
  2. Register a `Tool(...)` entry and its handler in
     `src/smartsheet_mcp/tools/__init__.py`.
  3. Use the shared helpers in `tools/_common.py` (`csv`, `pagination_params`).
  4. Be documented in `README.md`.

## Local setup

```bash
python3.10 -m venv .venv          # or python3.11/3.12
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the server

```bash
export SMARTSHEET_ACCESS_TOKEN="..."   # your dev token
smartsheet-mcp                         # stdio; stops on Ctrl+C
```

## Verifying a change

```bash
# Schema + handler integrity (runs offline)
python -c "from smartsheet_mcp.tools import TOOLS, HANDLERS; \
           assert set(t.name for t in TOOLS) == set(HANDLERS); \
           print(f'{len(TOOLS)} tools OK')"

# Live smoke test (uses real Smartsheet API)
SMARTSHEET_ACCESS_TOKEN=... python scripts/live_read_all.py
```

## Opening a pull request

1. Fork the project on GitHub.
2. Create a feature branch from `main`: `git checkout -b feat/your-change`.
3. Commit with a descriptive message.
4. Push and open a pull request with a clear description of the change and
   how you verified it.

## License

By contributing, you agree that your contributions will be licensed under the
project's [MIT License](LICENSE).
