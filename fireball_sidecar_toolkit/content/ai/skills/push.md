---
name: push
description: Use for pushing to git remote — runs invoke fix, invoke test, then commits and pushes. `/push all` runs the full push in every family repo. Equivalent to /push.
hints:
  - push all repos
  - push the repos
---

# Push Workflow
Use this file as source of truth: `.ai/toolkit/commands/push.md`

When the user asks to push changes, read that file and follow it. `/push all` runs the real
`/push` (fix + test + commit + push) in every repo in `properties.yml`'s `repos:` family —
confirm the repo list first and never skip a repo's tests. See the `repo` skill and
`.ai/toolkit/instructions/repos.md`.

```bash
uv run --no-sync python -m modules.toolkit.repo.push          # or: invoke repo.push --family
```

Same underlying module as `/repo push` — see the `repo` skill. If it fails at any stage (fix,
test, commit, push), show the full output to the user, explain which stage failed, and ask how
they'd like to proceed — do not retry automatically.
