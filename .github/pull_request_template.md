<!--
Thanks for contributing!

Before you submit, please confirm the following:
- [ ] No access tokens or customer data are included in this PR.
- [ ] Changes are read-only (or you have opened an issue first to discuss write scope).
- [ ] README / CHANGELOG updated if user-facing behaviour changed.
-->

## Summary

<!-- What does this change do? Why? -->

## How was it verified?

<!--
- Which tests / scripts did you run?
- Did you run `scripts/live_read_all.py` against a real token?
- Any edge cases exercised?
-->

## Checklist

- [ ] `ruff check .` passes
- [ ] `python -c "from smartsheet_mcp.tools import TOOLS, HANDLERS; assert set(t.name for t in TOOLS) == set(HANDLERS)"` passes
- [ ] No secrets committed
