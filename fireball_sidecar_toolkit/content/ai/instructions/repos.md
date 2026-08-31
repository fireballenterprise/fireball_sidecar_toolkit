---
description: "Use for the properties.yml repos/lineage key and the 'related repos' / 'pull all repos' / 'apply this across the repos' trigger phrases."
applyTo: "properties.yml,modules/setup/**"
---
# Repos Instructions
Rules for the `repos` key in `properties.yml` — the map of GitHub repos related to this repository —
and the `/repo` family commands built on it.

## Purpose
`properties.yml`'s `repos` key records which other GitHub repos are part of this vault's family
(grouped by org), plus a `lineage` sub-key recording parent → child template-stamping
relationships as a nested tree — e.g. `ai_vault` nested under `template_ai_vault` means `ai_vault`
was stamped from `template_ai_vault`. Bare repo names are used in the tree (no org prefix); a
repo's org is looked up from the flat org lists above it.

It's built additively, tier by tier, from `modules/setup/templates/properties/*.yml` — one fragment
file per repo in the lineage, each named after itself (`template_python.yml`,
`template_ai_python.yml`, `template_ai_vault.yml`, `ai_vault.yml`). Each fragment contributes only
its own org/repo + a `{parent: [self]}` lineage edge, deep-merged into one nested tree; a repo only
ever ends up knowing its own ancestor chain, never a sibling branch it isn't descended from. See
`modules/setup/README.md` and `docs/architecture.md#propertiesyml` for the build mechanism.

`properties.yml`'s sibling top-level `repos_local` key maps each org name (as used in `repos`) to
that org's local base directory on this machine (e.g. `fireballenterprise:
"$HOME/Development/fireballenterprise"`) — a repo's full local path is `repos_local.<org>/<repo>`.
This key is machine-specific (not part of the fragment-based build above) and should be kept
accurate whenever repos are cloned, moved, or renamed locally.

## "Related Repos" Trigger
When the user says **"related repos"**, **"the repos"**, **"other repos"**, **"all of the repos"**,
**"all the repos"**, **"pull all repos"**, **"pull the repos"**, or similar in the context of this
vault's repo family — not generic talk about "the repository" — **read this file in full before
acting**, then resolve the `repos` key in `properties.yml`. This applies whether or not the user
ran `/repo` — the phrase itself is the trigger.

Three distinct requests look similar but aren't:

- **"What are the related repos?"** — run `/repo list` (resolves and prints the `repos` / `lineage`
  map plus which clones exist locally). Nothing else.
- **"Pull all repos" / "pull the repos" / "pull the family"** — run `/repo pull all` (alias
  `/pull all`). It resolves `repos` + `repos_local`, and for each clone: `git stash -u` if dirty,
  switch to the **verified** default branch, `git fetch --prune`, `git pull --ff-only`, `git stash
  pop`. Read-only sync — no feature branches, no PRs. It prints a per-repo summary
  (updated / current / error). If `properties.yml` has no `repos:` map, it pulls just this repo
  and says so.
- **"Apply this to the related/other repos" / "apply this to all of the repos"** — the Cross-Repo
  Change Workflow below (`/repo apply`). Scope differs:
  - "related repos" / "other repos" — the *other* repos in the family; this repo is assumed
    already handled (e.g. its own PR already exists).
  - "all of the repos" / "all the repos" — **includes this repo too**. If this repo's own change
    isn't committed/pushed/PR'd yet, do that first (same format — commit, push, PR), then continue
    through the rest of the family in lineage order.

## The `/repo` family commands
- `/repo list` — the map (above).
- `/repo pull all` / `/pull all` — the read-only family sync (above). Implemented in
  `modules/toolkit/repo/family.py`, which verifies each repo's default branch via
  `gh repo view --json defaultBranchRef` and resets a stale `origin/HEAD`.
- `/repo push all` / `/push all` — runs the **real** `/push` (invoke fix + invoke test + commit +
  push) in every family repo, one at a time. It confirms the repo list first. Each repo's tests
  actually run — a repo whose tests fail is reported as failed and the run continues; surface
  every failure. This is not the Cross-Repo Change Workflow (no branches, no PRs) — it's for when
  each repo already has committed work on a tracked branch to push.
- `/repo cleanup all` / `/cleanup all` — per repo: clean up a merged feature branch, then sweep
  local build/cache trash + orphaned `modules/`/`tasks/`/`tests/` dirs. Never touches `topics/`
  or `tmp/`.
- `/repo apply <description>` — the Cross-Repo Change Workflow below.

Known `development`-default repos as of 2026-08-23: `fireball_3d_shopify`,
`fireball_powerups_shopify`, `fireball_sidecar_landing`, `fireball_sidecar_chat`,
`fireball_gear_shopify`. Everything else defaults to `main` — the `_landing`/`_shopify` naming
does not reliably predict it, so re-verify rather than assuming from the name.

## Cross-Repo Change Workflow (`/repo apply`)
When the user asks to apply a change (already made in this repo, or described fresh) to the related
repos, run it as **two phases with a checkpoint in between** — don't pipeline straight through to
pushing/PRs for every repo unattended.

### Phase 1 — Apply (no pushing yet)
1. Resolve which repos are in scope from `repos` / `lineage`. If the request is ambiguous about
   scope (all of them? just this branch? a specific sub-tree?), ask.
2. For each repo in scope, **in root-to-leaf lineage order** (a child repo may depend on its parent
   having the change first):
   a. Confirm its local clone exists at `repos_local.<org>/<repo>`.
   b. `git status` — if there are uncommitted changes, stash them (`git stash push -u`).
   c. Switch to the repo's **verified** default branch (see the known-`development` list above;
      `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, and
      `git remote set-head origin <branch>` if `origin/HEAD` disagrees).
   d. `git fetch --prune`, then pull the default branch up to date.
   e. Create a feature branch for this change.
   f. Apply the change — port the actual diff/pattern from the source repo/PR, or run the specific
      command/action the user named (e.g. `/update`). If it's unclear what a given repo's own tier
      fragment or config should contain (generic to its product line vs. real business config),
      **ask rather than guessing**.

### Checkpoint
Once the change is applied (uncommitted) in every repo in scope, stop and ask the user, e.g.:
"Made the changes in all N repos — ready to ship them, or is there more to add first?" Don't
proceed to Phase 2 until they confirm.

### Phase 2 — Ship
For each repo (same order), run the equivalent of `/ship-it`: fix, test, commit, push, draft PR
notes, open the PR (assigned to the user per `.ai/toolkit/instructions/git.md`'s Pull Request
Assignee rule). Report each repo's PR URL. Never merge a PR yourself, and never push directly to a
shared/default branch across multiple repos without being asked.

**Example:** "run `/update` on all the related repos" → Phase 1: for each repo in scope, cd in,
stash/switch/pull, branch, run `/update`. Checkpoint: confirm ready to ship. Phase 2: ship each
one — end state is one PR per repo, each showing that repo's own `/update` result, not one
combined PR.

The `pull all` / `push all` / `cleanup all` fan-outs are automated (`family.py`); the Cross-Repo
Change Workflow is not — each step is done directly (git commands + the repo's own test/push/PR
tooling).

## Module Implementation
Family resolution + fan-out: `modules/toolkit/repo/family.py` (+ `get_family_repos()` in
`modules/toolkit/setup/properties.py`). The `repos` build mechanism (tier fragments, additive
merge, no-op-if-exists): `modules/setup/README.md` and `modules/setup/properties.py`.
