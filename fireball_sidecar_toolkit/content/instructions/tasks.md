---
applyTo: "tasks/**"
---
# Tasks Instructions

## Overview

Invoke is the task runner for CICD workflows (fix, test, upgrade). All tasks are defined in `tasks/` and called via `uv run --no-sync invoke <task>`. Never use invoke for business logic — business logic lives in Python modules.

Unlike `.github/prompts/*.prompt.md` (which capture AI/human decision-making — see
`.github/instructions/logic.instructions.md`), invoke tasks are deterministic CLI automation only:
no judgment calls, no AI-specific behavior.

## Combo Tasks (use these most often)

| Task | Command | Description |
|------|---------|-------------|
| Fix | `uv run --no-sync invoke fix` | Run all auto-fixes (ruff fix + format) |
| Test | `uv run --no-sync invoke test` | Run all tests (actionlint + pylint + pytest + ruff + yamllint + toolkit drift check) |

## Test Tasks

| Task | Command | Description |
|------|---------|-------------|
| actionlint | `uv run --no-sync invoke tests.actionlint` | GitHub Actions workflow validation |
| pylint | `uv run --no-sync invoke tests.pylint` | Python code quality |
| pytest | `uv run --no-sync invoke tests.pytest` | Python unit test suite |
| rufflint | `uv run --no-sync invoke tests.rufflint` | Python linting and formatting |
| yamllint | `uv run --no-sync invoke tests.yamllint` | YAML file validation |

## Ruff Tasks

| Task | Command | Description |
|------|---------|-------------|
| fix | `uv run --no-sync invoke ruff.fix` | Auto-fix ruff lint issues |
| format | `uv run --no-sync invoke ruff.format` | Auto-format Python code |

## Upgrade Tasks

| Task | Command | Description |
|------|---------|-------------|
| libs | `uv run --no-sync invoke upgrade.libs` | Upgrade libraries only |
| python | `uv run --no-sync invoke upgrade.python` | Upgrade Python only |
| sync | `uv run --no-sync invoke upgrade.sync` | Sync dependencies (no version check) |
| upgrade | `uv run --no-sync invoke upgrade.upgrade` | Upgrade Python + all dependencies (default) |

## uv Tasks

| Task | Command | Description |
|------|---------|-------------|
| upgrade_bin | `uv run --no-sync invoke uv.upgrade_bin` | Upgrade the uv binary itself (`brew upgrade uv`) |
| upgrade_libs | `uv run --no-sync invoke uv.upgrade_libs` | Install the versions currently locked in `pyproject.toml` (`uv sync`) |

## Versioning Tasks

Read-only version-lock *checks* — compare `pyproject.toml` deps and `.github/workflows/` action
refs against latest releases and update the version locks in place (does not install anything;
see Upgrade Tasks above for that).

| Task | Command | Description |
|------|---------|-------------|
| update | `uv run --no-sync invoke ver.update` | Run every version check (libs, python, workflows) |
| libs | `uv run --no-sync invoke ver.libs` | Check `pyproject.toml` deps against latest releases |
| python | `uv run --no-sync invoke ver.python` | Check the pinned Python version against the latest release |
| workflows | `uv run --no-sync invoke ver.workflows` | Check `.github/workflows/` action refs against latest versions |
| upgrade | `uv run --no-sync invoke ver.upgrade` | Alias for `invoke upgrade.upgrade` (upgrade Python + all dependencies) |
| project_bump_patch | `uv run --no-sync invoke ver.project_bump_patch` | Bump root `VERSION` patch — every merge to development |
| project_bump_minor | `uv run --no-sync invoke ver.project_bump_minor` | Bump `VERSION` minor — a milestone release |
| project_bump_major | `uv run --no-sync invoke ver.project_bump_major` | Bump `VERSION` major — a major release |
| project_bump_build | `uv run --no-sync invoke ver.project_bump_build` | `VERSION` build counter — feature-branch only, never published |

## Invoke vs Direct Python

| Use case | Command |
|----------|---------|
| Fix code style | `uv run --no-sync invoke fix` |
| Run all tests | `uv run --no-sync invoke test` |
| Run one linter | `uv run --no-sync invoke tests.pylint` |
| Upgrade everything | `uv run --no-sync invoke upgrade.upgrade` |
| Run a module | `uv run --no-sync python -m modules.chat.start --title="..."` |
| Test a route | `uv run --no-sync python -m modules.chat.route "start my chat"` |

## Canonical Workflow

```bash
# After modifying Python or YAML files:
uv run --no-sync invoke fix    # auto-fix first
uv run --no-sync invoke test   # verify 10/10
```

All `uv run` calls MUST use `--no-sync`. See `.github/instructions/tests.instructions.md`.

## AI Provider Sync Tasks

Shared commands/instructions/skills come from `fireball_sidecar_toolkit`. The tasks are shipped by
the package and mounted under `sidecar.toolkit.*`:

| Task | Command | Description |
|------|---------|-------------|
| download | `uv run --no-sync invoke sidecar.toolkit.download` | clobber `_shared/` from the package, regenerate every provider file |
| check | `uv run --no-sync invoke sidecar.toolkit.check` | read-only drift gate (runs inside `invoke test`) |
| sync | `uv run --no-sync invoke sidecar.toolkit.sync` | inspect `_shared/` for local edits → offer upload → download |
| upload | `uv run --no-sync invoke sidecar.toolkit.upload` | open a PR against the toolkit with local `_shared/` edits |

Never hand-edit a generated provider file. See `prompts.instructions.md`.

## Ollama Tasks

| Task | Command | Description |
|------|---------|-------------|
| clean | `uv run --no-sync invoke ollama.clean` | Remove all downloaded models and blob cache |
| install | `uv run --no-sync invoke ollama.install` | Install Ollama + a local coding LLM |
| list | `uv run --no-sync invoke ollama.list` | List installed and available models |
| restart | `uv run --no-sync invoke ollama.restart` | Restart Ollama service via Homebrew |
| start | `uv run --no-sync invoke ollama.start` | Start Ollama service via Homebrew |
| status | `uv run --no-sync invoke ollama.status` | Show Ollama service and running-model status |
| stop | `uv run --no-sync invoke ollama.stop` | Stop Ollama service via Homebrew |
| uninstall | `uv run --no-sync invoke ollama.uninstall` | Uninstall Ollama and remove all models |
| update | `uv run --no-sync invoke ollama.update` | Update Ollama binary + all installed models |

## Task Ordering

Tasks within a file must be ordered **alphabetically by function name**. Do not order by addition date, logical grouping, or importance.

## Task File Locations

```
tasks/
├── combos.py        # fix, test combo tasks
├── debug.py         # debug utilities
├── ruff.py          # ruff.fix + ruff.format
├── setup.py         # setup.properties — creates/stamps properties.yml
├── tests.py         # actionlint, pylint, pytest, rufflint, yamllint
├── upgrade.py        # libs, python, sync, upgrade
├── uv.py            # uv.upgrade_bin, uv.upgrade_libs
└── versioning.py    # all, libs, workflows (version-lock checks)
```
