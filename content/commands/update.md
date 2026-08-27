---
name: update
description: Check pyproject.toml dependencies, the pinned Python version, and .github/workflows/ action refs against their latest published releases and update version locks. Does not install or run anything.
argument-hint: "[libs | python | workflows | update]"
agent: agent
---

Check for available version updates (read-only, makes no changes):

!`uv run --no-sync invoke ver.update --dry-run`

The output has three sections: a `pyproject.toml` dependency table (from `ver.libs`), a Python
version table (from `ver.python`), and a `.github/workflows/` action-ref table (from
`ver.workflows`). Any section may say everything is already up to date — treat that section as
done and move on.

## Which section(s) to act on

- `$ARGUMENTS` is `libs` → only act on the `pyproject.toml` section; ignore the others.
- `$ARGUMENTS` is `python` → only act on the Python version section; ignore the others.
- `$ARGUMENTS` is `workflows` → only act on the workflows section; ignore the others.
- `$ARGUMENTS` is `update`, or no arguments at all → walk through all three sections (this matches
  `uv run --no-sync invoke ver.update`, which is what the check above already ran).

## Applying an update

Show the user the relevant table exactly as printed, then ask whether to apply it.

- `pyproject.toml`: this only rewrites version constraints — it does NOT install anything. If the
  user says yes, run `uv run --no-sync invoke ver.libs --yes`, then tell them the locks were
  updated and that `uv run --no-sync invoke upgrade` will install them (do not run that yourself —
  installing is a separate, explicit step).
- Python version: this only rewrites config file references (`pyproject.toml`, `.python-version`,
  `.pylintrc`, `setup.sh`, `.github/actions/setup_uv/action.yml`) — it does NOT install a new
  Python or rebuild `.venv`. If the user says yes, run `uv run --no-sync invoke ver.python --yes`,
  then tell them the references were updated and that `uv run --no-sync invoke upgrade` will
  install the new version and rebuild `.venv`.
- `.github/workflows/`: this only rewrites `@ref` pins in the workflow files — it does NOT run any
  workflow. If the user says yes, run `uv run --no-sync invoke ver.workflows --yes`, then tell
  them the workflow files were updated and suggest reviewing the diff before committing.

If the user declines a section, make no changes for that section.
