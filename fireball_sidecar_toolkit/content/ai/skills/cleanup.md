---
name: cleanup
description: Use after a PR merges, or to tidy a repo — cleans up the merged feature branch (switch to default, pull, delete) then sweeps local build/cache trash and orphaned dirs. `all` does it across the family. Equivalent to /cleanup.
hints:
  - clean up the repo
  - clean up local trash
  - sweep stale caches
  - remove orphaned dirs
---

# Cleanup Workflow
Use this file as source of truth: `.ai/toolkit/commands/cleanup.md`

When the user asks to clean up after a merged PR, or to clear out local build/cache junk and
leftover directories from a refactor, read that file and follow it. Two phases: branch cleanup
(warn-and-skip if not applicable), then a local-trash sweep that lists everything and asks before
deleting. Never touches `topics/` or `tmp/`.

```bash
uv run --no-sync invoke repo.cleanup          # add --family for /cleanup all
```
