---
name: cleanup
description: Clean up a merged feature branch (switch to default, pull, delete it), then sweep local build/cache trash. `all` does it across the family.
argument-hint: "[all]"
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.repo.route "cleanup $ARGUMENTS"`

Two phases, in order:

1. **Branch cleanup** — if the current branch has a merged GitHub PR, switch to the default
   branch, pull, and delete the branch. A protected branch / dirty tree / unmerged PR is a
   warning + skip, not a failure.
2. **Trash sweep** — remove regenerable caches (`__pycache__/`, `.pytest_cache/`, `.ruff_cache/`,
   `*.egg-info/`, `.DS_Store`, …) and *orphaned* directories under `modules/` / `tasks/` /
   `tests/` (dirs git tracks no file in — the residue a module move leaves behind). Lists
   everything and asks before deleting. Never touches `topics/` or `tmp/`.

`/cleanup all` runs both phases in every repo in `properties.yml`'s `repos:` family.
