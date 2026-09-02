---
description: "Use when adding or editing an invoke task, or looking up the command for fix / test / upgrade / versioning / toolkit sync."
applyTo: "tasks/**"
---
# Tasks Instructions
Invoke is the task runner for CI/CD-style automation (fix, test, upgrade, version checks). Tasks
live in `tasks/` and run via `uv run --no-sync invoke <task>` (always `--no-sync`). Never put
business logic in a task — that lives in `modules/`. Unlike command bodies (which capture AI/human
judgment — see `.ai/toolkit/instructions/logic.md`), invoke tasks are deterministic: no judgment calls, no
AI-specific behavior.

## Most-Used
```bash
uv run --no-sync invoke fix    # ruff fix + format (+ changelog sync where present)
uv run --no-sync invoke test   # actionlint + pylint + pytest + rufflint + yamllint + toolkit drift check
```

## Task Groups
| Group | Tasks |
|---|---|
| `tests.*` | `actionlint`, `pylint`, `pytest`, `rufflint`, `yamllint` (repo-specific extras like `cfnlint` where applicable) |
| `ruff.*` | `fix`, `format` |
| `upgrade.*` | `libs`, `python`, `sync`, `upgrade` (Python + all deps) |
| `uv.*` | `upgrade_bin` (`brew upgrade uv`), `upgrade_libs` (`uv sync`) |
| `ver.*` | `update` (libs+python+workflows checks), `libs`, `python`, `workflows`, `upgrade` (alias), `project_bump_{patch,minor,major,build}` |
| `sidecar.toolkit.*` | `update`, `apply`, `upgrade`, `sync`, `contribute`, `check` — shipped by the `fireball_sidecar_toolkit` package (see below) |

Version checks (`ver.libs/python/workflows`) only rewrite the locks in `pyproject.toml` /
`.github/workflows/` — they don't install; `upgrade.*` does that. `--dry-run` / `--yes` on the
`ver.*` checks.

## AI Provider Sync (`sidecar.toolkit.*`)
Shared commands / instructions / skills come from `fireball_sidecar_toolkit`. The tasks are shipped
by the package and mounted under `sidecar.toolkit.*`:

| Task | Description |
|---|---|
| `update` | pull the newest toolkit release into the venv (`uv lock --upgrade-package` + `uv sync`) — nothing in the repo tree changes yet |
| `apply` | clobber `.ai/toolkit/` + `modules/toolkit/` + … from the **installed** package, regenerate every provider stub |
| `upgrade` | `update` then `apply` — take the new toolkit into this repo in one step |
| `sync` | `apply`, but stop first if `.ai/toolkit/` has local hand-edits (offer to `contribute` them) |
| `contribute` | open a PR against the toolkit with local `.ai/toolkit/` edits |
| `check` | read-only drift gate (runs inside `invoke test`) |
| `mdfix` | normalise every `*.md` (no blank after a header; no stray `---` in instruction bodies). `invoke fix` writes it, `invoke test` runs `mdfix --check` |

`download` / `upload` are kept as deprecated aliases for `apply` / `contribute`.

Never hand-edit a generated provider file. See `.ai/toolkit/instructions/ai_commands.md`.

## Conventions
- Tasks within a file are ordered **alphabetically by function name** — not by date or grouping
- `tasks/__init__.py` builds the root `Collection` — all task modules are wired explicitly, no
  auto-glob loading
- `modules/` are plain importable packages, imported directly by `tasks/*.py`
