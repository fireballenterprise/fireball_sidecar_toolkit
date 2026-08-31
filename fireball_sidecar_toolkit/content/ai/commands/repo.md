---
name: repo
description: Repo and repo-family operations — list the family map, pull/push/cleanup this repo or the whole family, or apply a change across it.
argument-hint: list | pull [all] | push [all] | cleanup [all] | apply <description>
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.repo.route "$ARGUMENTS"`

`/repo` with no subcommand prints usage. `pull` / `push` / `cleanup` act on the current repo; add
`all` to run across every repo in `properties.yml`'s `repos:` family (root-to-leaf lineage order).
With no `repos:` map, `all` falls back to just this repo and says so.

- **`/repo list`** — show the `repos:` / `lineage:` map and which clones exist locally.
- **`/repo cleanup [all]`** — clean up a merged feature branch (switch to the default branch,
  pull, delete it), then sweep local build/cache trash and orphaned `modules/`/`tasks/`/`tests/`
  directories. Never touches `topics/` or `tmp/`.
- **`/repo push all`** — runs the *real* `/push` (invoke fix + invoke test + commit + push) in
  each family repo. Confirm the repo list with the user first. Never skip a repo's tests; if a
  repo's tests fail, that repo is reported as failed and the run continues — surface every failure
  in your summary.
- **`/repo apply <description>`** — the two-phase Cross-Repo Change Workflow. Read
  `.ai/toolkit/instructions/repos.md` in full and follow it: apply the change on a feature branch
  in every family repo, stop at the checkpoint for the user, then ship one PR per repo.

Recognition trigger: when the user says "related repos", "the repos", "other repos", "all the
repos", "pull all repos", or similar about this vault's repo family — even without running
`/repo` — read `.ai/toolkit/instructions/repos.md` and act on it.
