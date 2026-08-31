---
description: "Use for the properties.yml repos: registry and the 'related repos' / 'pull all repos' / 'apply this across the repos' trigger phrases."
applyTo: "properties.yml,modules/setup/**"
---
# Repos Instructions
Rules for the `repos:` key in `properties.yml` — the registry of GitHub repos in this vault's
family — and the `/repo` family commands built on it.

## Schema
`repos:` is `org > repo_name > {attributes}`. Every repo carries the **same six keys** (no
omitting — a missing key must never be what a condition trips on):

| key | values | meaning |
|---|---|---|
| `ai` | `true` \| `false` | shares the AI-agent tooling layout (`.ai/` + generated provider dirs). Scope for propagating agent skills/instructions, not product code. |
| `default_branch` | `main` \| `development` | `development` ⇒ **two-branch dev→prd promotion** (feature work lands on `development`, `development`→`main` cuts a release). `main` ⇒ single-branch. |
| `parent` | a bare repo name in this map, or `none` | the repo this one was template-stamped from. `none` = a root. Resolves across orgs. |
| `purpose` | one line | what the repo is |
| `status` | `active` \| `retired` | `retired` = shelved. Kept in the map (so it's known context, not a mystery repo) but **excluded from every family fan-out**. |
| `visibility` | `public` \| `private` | GitHub visibility |

`repos_local:` (sibling top-level key) maps each org name to its local base directory
(`fireballenterprise: "$HOME/Development/fireballenterprise"`) — a repo's local path is
`repos_local.<org>/<repo>`. Machine-specific; keep it accurate as repos are cloned/moved.

A repo moved into an `_archive/` (or `archive/` / `tmp/`) directory under its org base dir is
invisible to every `/repo` command — that's how a retired local-only clone is parked.

> Legacy: some family repos still have the old `repos:` shape (`org: [names]` + a sibling
> `lineage:` tree). `get_family_repos()` reads both; migrate a repo to the schema above when you
> next touch its `properties.yml`. The tier-fragment builder
> (`modules/setup/templates/properties/*.yml` → `modules/setup/properties.py`) still emits the
> legacy shape on a fresh `inv setup.properties`; reconciling that is pending.

## "Related Repos" Trigger
When the user says **"related repos"**, **"the repos"**, **"other repos"**, **"all of the repos"**,
**"pull all repos"**, **"pull the repos"**, or similar about this vault's repo family — not generic
talk about "the repository" — **read this file before acting**, then resolve `repos:`. Applies
whether or not `/repo` was run.

Three distinct requests:

- **"What are the related repos?"** → `/repo list` (prints the `parent` tree + each repo's
  attributes + local-clone state). Nothing else.
- **"Pull all repos" / "pull the family"** → `/repo pull all` (alias `/pull all`). Per clone:
  `git stash -u` if dirty, switch to the **verified** default branch, `git fetch --prune`,
  `git pull --ff-only`, `git stash pop`. Read-only sync — no branches, no PRs. Per-repo summary.
  No `repos:` map ⇒ pulls just this repo and says so.
- **"Apply this to the related/other repos"** → the Cross-Repo Change Workflow below
  (`/repo apply`). "other/related repos" = the family minus this one (its own PR exists);
  "all of the repos" = includes this repo (do its own commit/push/PR first).

## `/repo` family commands
`/repo <verb>` acts on the current repo. A trailing **scope token** fans it across the family in
root-to-leaf `parent` order:

| scope | repos hit |
|---|---|
| `all` | the whole family |
| `ai` | `ai: true` |
| `dev_prd` | `default_branch: development` |

`status: retired` repos are **always skipped**. `/pull`, `/push`, `/cleanup` take the same scopes.

- `/repo pull <scope>` — the read-only family sync (above). `family.py` verifies each repo's
  default branch via `gh repo view --json defaultBranchRef` and resets a stale `origin/HEAD`.
- `/repo push <scope>` — runs the **real** `/push` (invoke fix + invoke test + commit + push) in
  each repo, one at a time; confirms the list first. Each repo's tests actually run — a repo whose
  tests fail is reported failed and the run continues; **surface every failure**. Not the
  Cross-Repo Change Workflow (no branches/PRs) — for when each repo already has committed work on a
  tracked branch to push.
- `/repo cleanup <scope>` — per repo: clean up a merged feature branch, then sweep local
  build/cache trash + orphaned `modules/`/`tasks/`/`tests/` dirs. Never touches `topics/`, `tmp/`,
  or untracked new work.
- `/repo apply <description>` — the Cross-Repo Change Workflow below.

## Cross-Repo Change Workflow (`/repo apply`)
Apply a change (made here, or described fresh) to the family as **two phases with a checkpoint** —
don't pipeline straight to pushing/PRs unattended.

### Phase 1 — Apply (no pushing yet)
1. Resolve the repos in scope from `repos:`. If scope is ambiguous (all? one sub-tree? `ai` only?),
   ask.
2. For each repo in scope, **in root-to-leaf `parent` order** (a child may need its parent's change
   first):
   a. Confirm its clone exists at `repos_local.<org>/<repo>`.
   b. `git status` — stash uncommitted changes (`git stash push -u`).
   c. Switch to its `default_branch` from `repos:` (verify against
      `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`; `git remote set-head origin
      <branch>` if `origin/HEAD` disagrees).
   d. `git fetch --prune`, pull that branch up to date.
   e. Create a feature branch.
   f. Apply the change — port the diff/pattern from the source, or run the command the user named
      (e.g. `/update`). If it's unclear what a repo's own config should hold (generic vs. real
      business config), **ask rather than guessing**.

### Checkpoint
Once applied (uncommitted) in every repo, stop: "Made the changes in all N repos — ready to ship,
or more to add first?" Don't proceed until they confirm.

### Phase 2 — Ship
For each repo (same order), run the equivalent of `/ship-it`: fix, test, commit, push, draft PR
notes, open the PR (assigned to the user per `.ai/toolkit/instructions/git.md`). Report each PR
URL. Never merge a PR yourself; never push to a shared/default branch across repos unasked.

**Example:** "run `/update` on all the related repos" → Phase 1: per repo, cd in, stash/switch/
pull, branch, `/update`. Checkpoint. Phase 2: ship each — one PR per repo showing that repo's own
`/update` result, not one combined PR.

The `pull` / `push` / `cleanup` fan-outs are automated (`family.py`); the Cross-Repo Change
Workflow is not — each step is done directly.

## Module Implementation
Family resolution + fan-out: `modules/toolkit/repo/family.py` + `get_family_repos()` in
`modules/toolkit/setup/properties.py`. Legacy tier-fragment build: `modules/setup/README.md` and
`modules/setup/properties.py`.
