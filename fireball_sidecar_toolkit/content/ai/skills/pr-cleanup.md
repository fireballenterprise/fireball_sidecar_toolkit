---
name: pr-cleanup
description: Use after a PR has been merged on GitHub — switches to the default branch, pulls, and deletes the merged local feature branch. Equivalent to /pr-cleanup.
---

# PR Cleanup Workflow
Use this file as source of truth: `.ai/toolkit/commands/pr-cleanup.md`

When the user asks to clean up after a merged PR, read that file and follow it.

```bash
uv run --no-sync invoke repo.pr_cleanup
```
