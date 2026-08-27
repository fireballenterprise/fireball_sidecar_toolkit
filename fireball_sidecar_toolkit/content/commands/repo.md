---
name: repo
description: Repo operations (push, pull, cleanup, set_screenshots, view_screenshot)
argument-hint: push | pull | cleanup | set_screenshots | view_screenshot
agent: agent
---

!`uv run --no-sync python -m modules.repo.route "$ARGUMENTS"`
