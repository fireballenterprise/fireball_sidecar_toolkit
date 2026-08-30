---
name: ship-it
description: Use for pushing the current feature branch and opening a Pull Request in one step. Equivalent to /ship-it. Also triggered by the phrases "punch it", "punch it chewy", or "ship it".
hints:
  - make it so
  - hit it number one
  - punch it
  - punch it chewy
  - ship it
---

# Ship It Workflow
Use this file as source of truth: `.ai/toolkit/commands/ship-it.md`

When the user says "punch it", "punch it chewy", "ship it", or otherwise asks to ship a branch
end-to-end, read that file and follow it.

It runs the push workflow, then drafts PR notes and opens a Pull Request. Stop and ask the user how
to proceed if the push stage fails — do not continue to the PR steps.
