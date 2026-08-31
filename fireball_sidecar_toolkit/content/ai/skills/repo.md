---
name: repo
description: Use for /repo — the family map (/repo list), pull/push/cleanup on this repo or the whole family (add `all`), or /repo apply to port a change across the family. Equivalent to /repo. Also the "related repos" / "pull all repos" trigger.
hints:
  - related repos
  - the repos
  - other repos
  - all of the repos
  - all the repos
  - pull all repos
  - pull all the repos
  - pull the repos
  - pull every repo
  - push all repos
  - the repo family
---

# Repo + Repo-Family Workflow
Use this file as source of truth: `.ai/toolkit/commands/repo.md`, and
`.ai/toolkit/instructions/repos.md` for the family map and the Cross-Repo Change Workflow.

- `/repo list` — show the `repos:` / `lineage:` family map.
- `/repo pull [all]`, `/repo push [all]`, `/repo cleanup [all]` — act on the current repo, or on
  every repo in the `repos:` family when `all` is given. `/pull`, `/push`, `/cleanup` are the
  short aliases and also take `all`.
- `/repo apply <description>` — the two-phase Cross-Repo Change Workflow.

When the user says "related repos", "the repos", "pull all repos", or similar about this vault's
repo family — even without running `/repo` — read `.ai/toolkit/instructions/repos.md` and act on
it. `push all` runs the real `/push` (fix + test + commit + push) per repo: confirm the list
first, never skip a repo's tests, and report every failure.

```bash
uv run --no-sync python -m modules.toolkit.repo.route "list"        # or "pull all", "push all", ...
```
