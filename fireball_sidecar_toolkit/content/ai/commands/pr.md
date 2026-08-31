---
name: pr
description: Draft PR notes for the current feature branch and open a Pull Request via gh (does not push).
argument-hint: no arguments required
agent: agent
---

If this repo is `pull_request: false` in `properties.yml` (`/repo self`), it ships by direct push,
not PRs — `pr_create` will refuse. Tell the user to use `/ship-it` (or push the default branch)
instead.

Gather the branch and diff context:

!`uv run --no-sync python -m modules.toolkit.repo.route "pr_diff"`

If that fails, show the full output to the user and ask how they'd like to proceed.

Using the branch, commit log, and diff above, write a Pull Request description (same as `/pr-notes`,
but do NOT save it to a file this time — just hold it in context):
- `## Summary` — 1-3 sentences describing the overall change
- `## Changes` — a bulleted list of the key changes (one bullet per logical change, not per file)

Then create the pull request:
1. Note the `Base branch:` value printed above.
2. Draft a concise PR title (under 70 characters) summarizing the change.
3. Run:
   `uv run --no-sync python -m modules.toolkit.repo.route "pr_create --title=\"<title>\" --content=\"<notes>\""`
4. Report the PR URL to the user.

If a PR already exists for this branch, `pr_create` reports its URL instead of erroring — just
relay that to the user.
