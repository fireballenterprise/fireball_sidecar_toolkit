---
name: test
description: Use for running all tests and linters — ruff, pylint, yamllint, actionlint, toolkit drift check. Equivalent to /test.
---

# Test Workflow

Use this file as source of truth: `.ai/shared/commands/test.md`

When the user asks to run tests/linters, or an equivalent `/test` request, read that file and
follow it.

```bash
uv run --no-sync invoke fix
uv run --no-sync invoke test
```

The required result is a 10.00/10 Pylint score with exit code 0 before committing.
