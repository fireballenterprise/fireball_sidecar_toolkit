---
name: fix
description: Use for auto-fix requests — run ruff check --fix and ruff format. Equivalent to /fix.
---

# Fix Workflow

Use this file as source of truth: `.github/prompts/fix.prompt.md`

When the user asks to auto-fix lint/formatting issues, or an equivalent `/fix` request, read that
prompt file and follow it.

```bash
uv run --no-sync invoke fix
```
