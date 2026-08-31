---
name: pull
description: Use for pulling updates from git remote — stash, pull --rebase, restore stash. `/pull all` pulls every repo in the family. Equivalent to /pull.
hints:
  - pull the latest
  - pull all repos
---

# Pull Workflow
Use this file as source of truth: `.ai/toolkit/commands/pull.md`

When the user asks to pull the latest changes, read that file and follow it. `/pull all` fans out
across `properties.yml`'s `repos:` family — see the `repo` skill and
`.ai/toolkit/instructions/repos.md`.

```bash
uv run --no-sync invoke repo.pull          # add --family for /pull all
```

Same underlying module as `/repo pull` — see the `repo` skill.
