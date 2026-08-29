---
name: push
description: Use for pushing the current branch to git remote — runs invoke fix, invoke test, then commits and pushes. Equivalent to /push.
---

# Push Workflow

Use this file as source of truth: `ai/shared/commands/push.md`

When the user asks to push changes, read that file and follow it.

```bash
uv run --no-sync python -m modules.repo.push
```

Same underlying module as `/repo push` — see the `repo` skill. If it fails at any stage (fix,
test, commit, push), show the full output to the user, explain which stage failed, and ask how
they'd like to proceed — do not retry automatically.
