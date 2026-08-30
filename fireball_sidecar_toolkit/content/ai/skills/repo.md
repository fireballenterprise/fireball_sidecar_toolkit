---
name: repo
description: Use for a generic /repo push|pull request — routes to the same push/pull workflows as the dedicated push and pull skills. Equivalent to /repo.
---

# Repo Router Workflow
Use this file as source of truth: `.ai/toolkit/commands/repo.md`

When the user asks for `/repo push` or `/repo pull` specifically, read that file and follow
it — it dispatches to the same modules as the dedicated `push` and `pull` skills.

```bash
uv run --no-sync python -m modules.toolkit.repo.route "push"   # or "pull"
```
