---
description: "Use for the properties.yml repos/lineage key and the 'related repos' / 'pull all repos' / cross-repo-change trigger phrases."
applyTo: "properties.yml,modules/setup/**"
---
# Repos Instructions
Rules for the `repos` key in `properties.yml` — the map of GitHub repos related to this repository.

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
**"all the repos"**, **"pull all repos"**, **"pull the repos"**, or similar in the context of this vault's repo family — not generic talk about
"the repository" — **read this file in full before acting**, then read the `repos` key in
`properties.yml` to know which other repos are part of this vault's family and how they're related.
This applies whether or not the user ran `/repos` — the phrase itself is the trigger.

Three distinct requests look similar but aren't:
- **"What are the related repos?"** — just resolve and show the `repos`/`lineage` map (`/repos`
  does this).
- **"Pull all repos" / "pull the repos" / "pull the family"** — for every repo in scope with a
  local clone (resolve paths from `repos_local`), bring it up to date: `git stash -u` if the
  tree is dirty, switch to its default branch, `git pull --ff-only`, then `git stash pop` if
  you stashed. Read-only sync, **not** the Cross-Repo Change Workflow below — no feature
  branches, no PRs. Report each repo's result (updated / already current / skipped-dirty /
  conflict).
- **"Apply this to the related/other repos"** vs. **"apply this to all of the repos"** — both run
  the Cross-Repo Change Workflow below, but scope differs:
  - "related repos" / "other repos" — the *other* repos in the family; this repo is assumed already
    handled (e.g. its own PR already exists).
  - "all of the repos" / "all the repos" — **includes this repo too**. If this repo's own change
    isn't committed/pushed/PR'd yet, do that first (same format as every other repo — commit, push,
    PR), then continue through the rest of the family in lineage order.

## Cross-Repo Change Workflow
When the user asks to apply a change (already made in this repo, or described fresh) to the related
repos, run it as **two phases with a checkpoint in between** — don't pipeline straight through to
pushing/PRs for every repo unattended.

### Phase 1 — Apply (no pushing yet)
1. Resolve which repos are in scope from `repos`/`lineage`. If the request is ambiguous about scope
   (all of them? just this branch? a specific sub-tree?), ask.
2. For each repo in scope, **in root-to-leaf lineage order** (a child repo may depend on its parent
   having the change first — e.g. `/template` pulling it down):
   a. Confirm its local clone exists at `repos_local.<org>/<repo>` (from this repo's own
      `properties.yml`).
   b. `git status` — if there are uncommitted changes, stash them (`git stash push -u`) rather than
      losing or clobbering in-progress work.
   c. Switch to the repo's default branch — **don't assume `main`**. Several repos in the family
      default to `development` instead, and a local clone's `origin/HEAD` can go stale (still
      pointing at `main`) even when GitHub's default branch is `development`, causing a naive pull
      to silently check out the wrong branch. Verify with
      `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` (or check `git symbolic-ref
      refs/remotes/origin/HEAD` and fix it with `git remote set-head origin <branch>` if it
      disagrees). Known `development`-default repos as of 2026-08-23: `fireball_3d_shopify`,
      `fireball_powerups_shopify`, `fireball_sidecar_landing`, `fireball_sidecar_chat`,
      `fireball_gear_shopify`. Everything else in the family (including `fireball_enterprise_landing`,
      `template_shopify`, `workflows_shopify`) defaults to `main` — the `_landing`/`_shopify` naming
      does not reliably predict it, so re-verify rather than assuming from the name.
   d. `git fetch --prune`, then pull the default branch up to date.
   e. Create a feature branch for this change.
   f. Apply the change in that repo — either port the actual diff/pattern from the source repo/PR,
      or run the specific command/action the user named (e.g. `/update`), whichever the request
      calls for. If it's unclear what a given repo's own tier fragment or config should contain
      (e.g. what's generic to that repo's product line vs. real business config), **ask rather than
      guessing**.

### Checkpoint
Once the change is applied (uncommitted) in every repo in scope, stop and ask the user, e.g.: "Made
the changes in all N repos — ready to ship them, or is there more to add first?" Don't proceed to
Phase 2 until they confirm.

### Phase 2 — Ship
For each repo (same order), run the equivalent of `/ship-it`: fix, test, commit, push, draft PR
notes, open the PR (assigned to the user per `git.instructions.md`'s Pull Request Assignee rule).
Report each repo's PR URL back to the user. Never merge a PR yourself, and never push directly to a
shared/default branch across multiple repos without being asked.

**Example:** "run `/update` on all the related repos" → Phase 1: for each of the (e.g. 7) repos in
scope, cd in, stash/switch/pull, branch, run `/update`. Checkpoint: confirm ready to ship. Phase 2:
ship each one — end state is one PR per repo, each showing that repo's own `/update` result, not one
combined PR.

No dedicated automation exists for this yet (as of 2026-08-01) — each step above is done directly
(git commands, the repo's own test/push/PR tooling), not via a single script.

## Module Implementation
For the build mechanism (tier fragments, additive `repos` merge, no-op-if-exists behavior), see
`modules/setup/README.md` and `modules/setup/properties.py`.
