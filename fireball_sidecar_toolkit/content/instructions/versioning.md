---
description: "Use when working with the modules/versioning/ package — bumping the repo's VERSION file for releases, or checking/updating dependency version locks and GitHub Actions action-ref pins."
applyTo: "modules/versioning/**"
---
# Versioning Instructions
## Project VERSION Bumps (`project.py`)
The root `VERSION` file is the **single source of truth** for this repo's version — plain
`Major.Minor.Patch`, no build suffix, on `development` and `main`. `pyproject.toml` reads it via
`[tool.setuptools.dynamic]` (`version = { file = "VERSION" }`); never hand-write a `version =` in
`[project]`. This is separate from this directory's `libs.py`/`workflows.py` checks (dependency
locks and Action ref pins — see below).

**Scheme (family-wide, 2026-08-28):**
- **Every merge to `development`** → `ver.project_bump_patch` (`0.2.0` → `0.2.1`). In dev→`main`
  repos with CI this is automatic (`version.yml`); elsewhere it's a manual step.
- **A release** just **promotes `development` → `main` and tags the current `VERSION`** — no bump.
  Force a milestone with the release workflow's `bump` input: `ver.project_bump_minor`
  (`0.2.7` → `0.3.0`) or `ver.project_bump_major` (the eventual official `1.0.0`).
- **Feature branches** may use `ver.project_bump_build` (`0.2.1` → `0.2.1-001` → `-002`) as a local
  build counter. A build suffix is **never** merged to `development` or published.

```sh
uv run --no-sync invoke ver.project_bump_patch      # every merge to development
uv run --no-sync invoke ver.project_bump_minor      # milestone release (release workflow bump=minor)
uv run --no-sync invoke ver.project_bump_major      # major release (release workflow bump=major)
uv run --no-sync invoke ver.project_bump_build      # feature-branch build counter only, never published
```
All four only rewrite `VERSION` — no commit, branch, push, tag, or workflow trigger. `project.py`
exposes `bump_patch()`/`bump_minor()`/`bump_major()`/`bump_build()` and a `python -m
modules.versioning.project [patch|minor|major|build]` CLI. It has its **own** `get_repo_root()`
keyed on `pyproject.toml` + `VERSION` — not `modules.common.properties.get_repo_root()`, which
searches for the git-ignored `properties.yml` and fails in CI where `version.yml`/`release.yml`
runs these tasks.

## Dependency/Action Version Checks (`libs.py`, `python.py`, `workflows.py`)
Three checks against external sources of truth, plus the installs that follow (`upgrade.py`):
- `ver.libs` — compares `pyproject.toml`'s `[project.dependencies]` against the latest
  published package releases (via `uv pip list [--outdated]`), and rewrites just the version locks
- `ver.python` — compares the pinned Python version against the latest stable 3.x release, and
  rewrites the config file references (does not install)
- `ver.workflows` — compares `.github/workflows/*.yml`'s `uses: owner/repo@vN` refs against
  the latest major tag published on GitHub for that action, and rewrites just the ref pins

See `modules/versioning/README.md` for full behavior/data-flow details on each.

```sh
uv run --no-sync invoke ver.libs        # check + prompt to update pyproject.toml locks
uv run --no-sync invoke ver.python      # check + prompt to update the pinned Python version
uv run --no-sync invoke ver.workflows    # check + prompt to update workflow action refs
uv run --no-sync invoke ver.update       # libs + python + workflows together (same as top-level `update`)
uv run --no-sync invoke ver.libs --dry-run   # preview only, never writes (also on python/workflows/update)
uv run --no-sync invoke ver.libs --yes       # skip the confirmation prompt (also on python/workflows/update)

uv run --no-sync invoke ver.upgrade      # install the upgrades reviewed above (same as top-level `upgrade`)
```
`/update [libs | python | workflows]` runs all three checks and walks through applying them;
`/upgrade` executes the actual installs afterward.

### Relationship to Other Workflows
- `ver.libs` only edits `pyproject.toml` — run `uv run --no-sync invoke upgrade.libs`
  (`uv sync --upgrade`) afterward to actually install the new versions
- `ver.python` only edits config file references — run `uv run --no-sync invoke upgrade.python`
  afterward to install the new Python and rebuild `.venv`
- `ver.workflows` only edits `.github/workflows/*.yml` — run
  `uv run --no-sync invoke tests.actionlint` afterward to confirm nothing broke

`libs.py`/`python.py`/`workflows.py` use `@click.command()` with `--dry-run`/`--yes` options.

## Module Conventions
Same conventions as `.ai/shared/instructions/modules.md` and
`.ai/shared/instructions/python.md` — `main()`-style entry points, subprocess/`print()`/
type-hint rules — not restated here.
