---
name: pr
description: Use for drafting PR notes and opening a Pull Request via gh for the current feature branch (does not push). Equivalent to /pr.
---

# Open PR Workflow
Use this file as source of truth: `.ai/toolkit/commands/pr.md`

When the user asks to open a pull request, read that file and follow it.

```bash
uv run --no-sync invoke repo.pr_diff
uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"
```

This drafts notes and opens the PR but does not push first — push separately (see the `push`
skill) if the branch isn't already up to date on the remote. The PR is assigned to the calling
user (`--assignee @me`). If a PR already exists for this branch, `repo.pr_create` reports its URL
instead of erroring.
