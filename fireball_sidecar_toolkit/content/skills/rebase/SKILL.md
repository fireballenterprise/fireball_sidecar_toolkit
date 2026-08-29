---
name: rebase
description: Use for rebasing the current branch onto the remote default branch, optionally squashing first. Equivalent to /rebase.
---

# Rebase Workflow

Use this file as source of truth: `.github/prompts/rebase.prompt.md`

When the user asks to rebase onto the default branch, read that prompt file and follow it.

```bash
uv run --no-sync invoke repo.rebase
```
