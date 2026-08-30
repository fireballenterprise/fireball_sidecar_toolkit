---
name: docs
description: Use for auditing the repo for doc/AI-config drift after changes and fixing anything stale — READMEs, .ai/toolkit/ + .ai/<repo>/, AGENTS.md, CLAUDE.md, and the generated provider dirs. Equivalent to /docs.
---

# Docs Drift Audit Workflow
Use this file as source of truth: `.ai/toolkit/commands/docs.md`

When the user asks to audit docs, check for stale documentation, or run a `/docs` equivalent, read
that file and follow it.

Gather what changed on this branch:

```bash
uv run --no-sync invoke repo.pr_diff
```

Then sweep every doc/AI-config surface it lists — root `README.md`, module `README.md`s,
`.ai/toolkit/instructions/*.md` + `.ai/<repo>/instructions/*.md`, `AGENTS.md`/`CLAUDE.md`, and any
example/config file describing setup — and fix anything the change made stale directly. This is a
repo-local consistency sweep, so no confirmation is needed before editing.
