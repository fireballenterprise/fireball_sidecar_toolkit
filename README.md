# fireball_sidecar_toolkit
[![Tests](https://github.com/fireballenterprise/fireball_sidecar_toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/fireballenterprise/fireball_sidecar_toolkit/actions/workflows/tests.yml)

Single source of truth for the shared AI-agent tooling. Canonical slash commands, agent
instructions, and skills live here as tool-neutral markdown under
`fireball_sidecar_toolkit/content/`; each consuming repo mirrors that into `.ai/toolkit/` (its own
repo-specific additions live in `.ai/<repo>/`). A generator renders a pointer stub for every AI tool
(`.claude/`, `.github/prompts/`, `.github/instructions/`, `.clinerules/`, `.sidecar/`, `AGENTS.md`)
back to the `.ai/` source.

See [DESIGN.md](DESIGN.md) for the architecture, branch model, and open questions.

## Use it in a repo
```toml
# pyproject.toml — stable channel (floating major tag on main; @0 pre-1.0, @1 after launch)
[dependency-groups]
dev = ["fireball_sidecar_toolkit @ git+https://github.com/fireballenterprise/fireball_sidecar_toolkit@0"]
# dev channel: ...@development
```
```sh
uv run --no-sync invoke sidecar.toolkit.update      # uv lock --upgrade-package + uv sync (pull the newest release into the venv)
uv run --no-sync invoke sidecar.toolkit.apply       # clobber .ai/toolkit/ etc. from the installed package, regenerate
uv run --no-sync invoke sidecar.toolkit.upgrade     # update + apply — take the new toolkit in one step
uv run --no-sync invoke sidecar.toolkit.sync        # apply, but stop first if .ai/toolkit/ has local hand-edits
uv run --no-sync invoke sidecar.toolkit.contribute  # open a PR here with local .ai/toolkit/ changes
uv run --no-sync invoke sidecar.toolkit.check       # read-only drift gate (wire into invoke test / CI)
uv run --no-sync invoke sidecar.toolkit.mdfix       # normalise *.md (no blank after header, no stray ---); --check to gate
```
`download` / `upload` are kept as deprecated aliases for `apply` / `contribute`.
No dependency wanted (non-Python repo): `uvx --from git+https://github.com/fireballenterprise/fireball_sidecar_toolkit sidecar-toolkit apply`.

## Consuming-repo contract
| path | rule |
|------|------|
| `.ai/toolkit/` | clobbered copy of the toolkit's `content/` — never hand-edit |
| `.ai/<repo>/` | this repo's own `instructions/ commands/ skills/` — never synced |
| `modules/toolkit/`, `tasks/toolkit/`, `tests/toolkit/` | clobbered copies of `content/{modules,tasks,tests}/` — shared Python (`modules.toolkit.*`) |
| `setup.sh`, `setup.ps1` | clobbered from `content/scripts/` — repo extras go in `setup.local.sh` (never clobbered) |
| `.claude/`, `.github/{prompts,instructions,skills,copilot-instructions.md}`, `.clinerules/`, `.sidecar/`, `AGENTS.md`, `CLAUDE.md` | generated pointer stubs → `.ai/` — never hand-edit |
| `.sidecar-toolkit.yml` (optional) | `vendor: [ai, scripts]` — take only some shipped trees (`ai`, `modules`, `tasks`, `tests`, `scripts`); absent = all |

Fix shared behavior by editing `content/` here, or by editing `.ai/toolkit/` in a consuming repo and
running `sidecar.toolkit.contribute` to open a PR.

## Branch model
`development` (integration, PRs merge here) → promoted to `main` (stable) via
`sidecar.toolkit.release`, which tags a release. Consumers pin `@0` (stable, pre-1.0) → `@1` after launch or `@development`
(nightly). PyPI publishing lands once release workflows are usable (after 2026-09-01).

## Development
```sh
./setup.sh
uv run --no-sync invoke fix
uv run --no-sync invoke test
```
