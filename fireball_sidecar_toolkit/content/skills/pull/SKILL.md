---
name: pull
description: Use for pulling updates from this repo's git remote — stash, pull --rebase, restore stash. Equivalent to /pull.
---

# Pull Workflow

Use this file as source of truth: `.github/prompts/pull.prompt.md`

When the user asks to pull the latest changes from git remote, read that prompt file and follow it.

```bash
uv run --no-sync invoke repo.pull
```

Same underlying module as `/repo pull` — see the `repo` skill.
