---
name: template
description: Pull shared tooling updates from the parent template repo into this project (default), or push new generic tooling from this project into the parent template repo as a PR (template push).
argument-hint: "[pull|push]"
agent: agent
---

If `$ARGUMENTS` is empty or "pull", do a **Pull**. If `$ARGUMENTS` starts with "push", do a **Push**.

Locate the shared template repo:

!`uv run --no-sync python -m modules.template.route`

The line above starting with `TEMPLATE_PATH=` is the resolved local path to the template repo
(cloned to `tmp/template_sync/` if it wasn't found locally). Both Pull and Push use this path.

## Pull

Compare that template repo against this project and sync it in:

1. **Always exclude** (never touch, even if present in the template repo): `properties.yml`,
   `README.md`, `LICENSE`, `uv.lock`, `pyproject.toml`, `.claude/settings.local.json`, `.git/`,
   `.venv/`, `__pycache__/`, `.ruff_cache/`, any other cache/build artifact, anything under
   `logs/` or `tmp/`, and this project's own content directories (`topics/`, `agents/`, `docs/`,
   `screenshots/`, `active_topic.yml`) — the template repo has no equivalent of these, but never
   touch them regardless.
2. **Shared tooling — sync these by default** if present in the template repo: `modules/`,
   `tasks/`, `.github/instructions/`, `.github/prompts/`, `.github/workflows/`,
   `.claude/commands/`, `.vscode/`, `invoke.yml`, `setup.sh`, `CLAUDE.md`, `.editorconfig`,
   `.yamllint`. Also look at anything else at the template repo's top level not covered by the
   exclude list — use judgment on whether it's generic tooling or project-specific, and ask the
   user if genuinely unsure.
3. For each candidate file:
   - Missing in this project → propose adding it.
   - Identical to what's already here → skip silently.
   - Different from what's already here → show a short diff and ask the user whether to
     overwrite, keep the local version, or merge by hand. Do not overwrite silently.
   - Note: this project also maintains `.opencode/command/`, generated from `.github/prompts/`
     via `uv run --no-sync invoke opencode.sync` — never delete or skip-sync it based on the
     template repo's absence; regenerate it per step 5 instead.
4. Apply only the changes the user approved (plus unambiguous additions/identical-skips), then
   summarize what was added, updated, and skipped.
5. If `.github/prompts/` changed, remind the user to run `uv run --no-sync invoke opencode.sync`
   (add `--force` to overwrite hand-crafted `.opencode/command/` files) afterward — do not run it
   automatically. Also remind them to hand-update `.claude/commands/` and `.clinerules/workflows/`
   to match (no sync script for those — see `.github/instructions/prompts.instructions.md`) and
   run `uv run --no-sync invoke tests.check_agents` to confirm all four mirrors stay in sync.

Never modify `pyproject.toml`, `properties.yml`, `README.md`, `LICENSE`, or `uv.lock` even if the
template repo's versions differ from this project's — those are always project-specific and must
be reconciled by hand.

## Push

Push proposes NEW generic improvements made in this repo into its parent template repo as a pull
request. Only genuinely generic, non-business content may be proposed — never financials/
personal-finance content.

**Scope** (enforced by `modules/template/scope.py`, mirrored here for visibility):
- Eligible directories: `modules/`, `.github/instructions/`, `.github/prompts/`,
  `.claude/commands/`, `.claude/skills/`, `.clinerules/workflows/`, `.opencode/command/`.
- Candidates come from `git ls-files`, so anything this repo's own `.gitignore` covers is already
  excluded — nothing hardcoded for that.
- Also excluded: anything in this project's `template.ignore.yml` `exclude:` list — the same file
  `/template pull` uses to protect project-specific content, applied here in the other direction so
  it never leaks upstream either. Business modules or personal-vault content (e.g.
  `modules/financials/`, `.claude/skills/financials/`) are declared there once instead of being
  hardcoded in Python.

Repo-name references are rewritten automatically on copy (this repo's name → the template repo's
name, both derived from `properties.yml` `repo.local`/`template.local` basenames), so name-only
differences never need hand-editing and never count as modifications.

**Steps:**

1. Using the Bash tool, run `uv run --no-sync python -m modules.template.route "push diff"`.
   This clones/updates the template default branch and prints three scope-filtered lists:
   - `ADDED:` — in this repo, missing from the template.
   - `MODIFIED:` — differs from the template after repo-name rewriting.
   - `DELETED:` — in the template but no longer in this repo. These are deprecation candidates
     only; nothing is deleted without explicit approval in step 3.
2. Review all three lists and assemble the FULL change set for one complete PR:
   - Pair up renames: an ADDED file that replaces a DELETED one (e.g. a renamed command) should
     ship together — the add and the delete in the same PR, plus a scan of the template's docs
     for now-dangling references to the deleted name (fix those template-side files in step 4's
     review if needed).
   - Only propose a deletion when its replacement is included in this PR or the file is clearly
     obsolete. When unsure whether something is deprecated or template-specific, ask the user.
   - For borderline generic-vs-business content not already covered by the fixed exclusion list,
     ask the user before including it. Drop anything the user doesn't want.
3. Show the user the final change set — files to add, update, and delete — with a one-line
   summary of what changed, and ask them to confirm proposing it to the template repo.
4. If approved, using the Bash tool, run (once, with one `--file` per approved copy and one
   `--delete` per approved removal):
   `uv run --no-sync python -m modules.template.route "push apply --file <path1> --file <path2> --delete <path3> ..."`
   This resolves/updates the local template checkout, creates a new branch, copies the approved
   files (with repo-name rewriting), applies the deletions, commits, and pushes the branch — it
   does **not** open a PR yet. Note the `TEMPLATE_PUSH_BRANCH=` and `TEMPLATE_PUSH_BASE=` values
   it prints. `--delete` refuses paths outside the push scope.
5. Show the user the pushed branch name and propose a PR title/body covering adds, updates, AND
   deletions. **Explicitly ask the user to confirm before opening the PR** — do not proceed
   without an explicit "yes".
6. Only after confirmation, using the Bash tool, run:
   `uv run --no-sync python -m modules.template.route "push create-pr --branch <branch> --title \"...\" --body \"...\""`
   This opens the PR against the template repo via `gh pr create`.
