---
name: squash
description: Use for an anchored squash of all commits to the root commit, with confirmation and optional force push. Equivalent to /squash.
---

# Squash Workflow

Use this file as source of truth: `.github/prompts/squash.prompt.md`

When the user asks to squash all commits to the root, read that prompt file and follow it.

```bash
uv run --no-sync invoke repo.squash
```
