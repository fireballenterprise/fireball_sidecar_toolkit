---
description: "Use when working with the modules/versioning/ package — bumping the repo's VERSION file for releases, or checking/updating dependency version locks and GitHub Actions action-ref pins."
applyTo: "modules/versioning/**"
---
# Versioning Instructions

## Project VERSION Bumps (`project.py`)

The root `VERSION` file tracks this repo's release version — what gets tagged as a GitHub
Release, if this repo ships one. This is separate from `pyproject.toml`'s own `[project]
version` field (Python package metadata, unrelated) and from this same directory's `libs.py`/
`workflows.py` checks (dependency locks and GitHub Action ref pins against external sources — a
different concern, see below).

Scheme: `Major.Minor.Patch[-Build]`
- No build suffix (e.g. `1.0.0`) — a released version.
- A build suffix (e.g. `1.1.0-003`) — build `003` toward `1.1.0`, in progress but not yet released.

Two operations, one per `ver.project_bump_*` invoke task:
- `ver.project_bump_build` — no build suffix yet -> bump the minor and start build `001`
  (`1.0.0` -> `1.1.0-001`); build suffix present -> increment the build number only
  (`1.1.0-001` -> `1.1.0-002`)
- `ver.project_bump_release` — drop the build suffix (`1.1.0-003` -> `1.1.0`)

See `modules/versioning/README.md` for full behavior/data-flow details.

```sh
uv run --no-sync invoke ver.project_bump_build      # dev build: new minor's first build, or next build number
uv run --no-sync invoke ver.project_bump_release    # release: drop the build suffix
```
Both only rewrite `VERSION` — they don't commit, branch, or push, tag a release, or trigger any
workflow. This repo has no `deploy.yml`/`release.yml` of its own; a project that adds one should
wire it to call these tasks.

`project.py` exposes `bump_build()`/`bump_release()` (public, no leading `_`) as the underlying
functions, plus a `@click.command()` `main()` with a `--release` flag so the invoke tasks can
invoke it via `python -m modules.versioning.project [--release]` — this module follows the
subprocess-invocation convention used by `libs.py`/`python.py`/`workflows.py` in this repo (unlike
the direct-import style used elsewhere), since `tasks/*.py` here never imports `modules` directly.
Resolve the repo path via `modules.common.properties.get_repo_root()`, not `get_repo_local()` —
these tasks may run in CI, where `get_repo_local()`'s hardcoded local-machine path doesn't exist.

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
Same conventions as `.github/instructions/modules.instructions.md` and
`.github/instructions/python.instructions.md` — `main()`-style entry points, subprocess/`print()`/
type-hint rules — not restated here.
