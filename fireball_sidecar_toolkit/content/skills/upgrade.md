---
name: upgrade
description: Use for upgrading the project's Python version and/or dependencies. Equivalent to /upgrade.
---

# Upgrade Workflow

Use this file as source of truth: `.ai/shared/commands/upgrade.md`

When the user asks to upgrade Python or dependencies, read that file and follow it. Prefer
running `/update`-equivalent checks first (see the `update` skill) unless the user explicitly asks
to upgrade directly.

Run the appropriate module command exactly as the source prompt specifies for the requested scope
(`python` or `libs`).
