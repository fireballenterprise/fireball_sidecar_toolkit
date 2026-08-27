---
description: "Use when reviewing a pull request or code change in this repo — including automated PR review. Covers what to prioritize and what to skip."
---
# Review Instructions

## Priorities (in order)
1. **Logic correctness** — trace the actual code paths changed, don't just skim the PR
   description. Flag off-by-one errors, unhandled edge cases, incorrect conditionals, silent
   failures, and mismatched types. If a function's behavior changed, confirm every caller still
   gets what it expects.
2. **DRY / duplication** — flag near-duplicate logic that belongs in a shared helper (see
   `modules/common/` in `.github/instructions/modules.instructions.md`), and duplicated
   constants/strings that should be defined once.
3. **Docs kept in sync** — if the diff touches a module, command, task, or config key, the
   matching `README.md` and the relevant `.github/instructions/*.md` file must reflect it (see
   `.github/instructions/modules.instructions.md`). A PR that adds or edits a
   `.github/prompts/*.prompt.md` command without updating all five synced dirs (see below) is
   incomplete.
4. **Style compliance** — see `.github/instructions/style.instructions.md`. Flag violations even
   where `invoke test` would still pass — some of these are conventions, not lint-enforced rules.
5. **Tests/linters** — see `.github/instructions/tests.instructions.md`. Any `.py`, `.yml`, or
   `.yaml` change must be clean under `uv run --no-sync invoke test` (pylint 10.00/10 required),
   and `uv run --no-sync invoke tests.pytest` must pass.

## Repo-Specific Consistency Checks
- `.github/instructions/` is this repo's source of truth for all AI/agent rules — a PR that
  changes behavior without updating the relevant instruction file is incomplete, not just
  under-documented.
- The five synced command/skill dirs (`.github/prompts/`, `.claude/commands/`, `.claude/skills/`,
  `.clinerules/workflows/`, `.opencode/command/`) must stay behaviorally consistent — see
  `.github/instructions/prompts.instructions.md` and `skills.instructions.md`. Flag a PR that edits
  some but not all five; `uv run --no-sync invoke tests.check_agents` confirms they match.

## What NOT to Flag
- Formatting nitpicks `ruff format` already enforces — don't re-litigate what the tool owns.
- Missing tests/lint conformance inside `topics/` — that content is excluded from this repo's own
  lint/test surface by design (see `extend-exclude`/`exclude` in `pyproject.toml`).
