---
name: update
description: Use for checking dependency, Python, and workflow-action versions against latest releases and updating version locks — read-only, never installs or upgrades. Equivalent to /update.
---

# Update Workflow

Use this file as source of truth: `ai/shared/commands/update.md`

When the user asks for version checks, read that file and follow it — this only updates
locks, it never installs anything or runs an upgrade.

```bash
uv run --no-sync invoke ver.all
```

Run `/update`-equivalent checks before any `/upgrade` unless the user explicitly asks to upgrade
directly (mirrors `apt update && apt upgrade`) — see the `upgrade` skill.
