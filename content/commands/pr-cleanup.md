---
name: pr-cleanup
description: Switch to the default branch, pull, and delete the merged local feature branch.
argument-hint: no arguments required
agent: agent
---

!`uv run --no-sync python -m modules.repo.route "pr_cleanup"`
