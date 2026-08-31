---
name: backlog
description: Use for tracking bugs / features / tasks as GitHub Issues on any repo in the family — filing, listing, viewing, working, commenting, closing. Equivalent to /backlog (and the /add_bug, /add_feature, /add_task aliases).
hints:
  - file a bug
  - log a bug
  - track a bug
  - feature request
  - add to the backlog
  - known issue
  - list the issues
  - show the bugs
  - what's open in
  - any bugs in
  - work on issue
  - pick up issue
  - fix this bug
  - fix the next issue
  - fix all the open issues
  - knock out the backlog
  - close issue
  - mark it shipped
---

# Backlog (GitHub Issues)
Source of truth: [.ai/toolkit/commands/backlog.md](.ai/toolkit/commands/backlog.md).

Fires when the user wants to file, list, view, work, comment on, or close a bug / feature / task
for **any repo in the family** — "file a bug in sidecar vscode", "list the open issues for the
toolkit", "work on issue 12 in vscode", "fix all the open bugs in chat". Read the command file
and follow its **Recognition** table, **Issue body format**, and **Guardrails** (scrub secrets
before any write; confirm batches; honour each repo's `properties.yml` ship rules; one issue per
branch). The `invoke backlog.*` tasks are the CRUD layer; this skill carries the
resolve-repo then work then ship then close flow.
