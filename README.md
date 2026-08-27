# fireball_sidecar_toolkit
[![Tests](https://github.com/fireballenterprise/fireball_sidecar_toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/fireballenterprise/fireball_sidecar_toolkit/actions/workflows/tests.yml)

Single source of truth for the shared AI-agent tooling. Canonical slash commands, agent
instructions, and skills live here as tool-neutral markdown under
`fireball_sidecar_toolkit/content/`; a generator renders them into every AI tool's native format
(`.claude/`, `.github/prompts/`, `.github/instructions/`, `.clinerules/`, `.opencode/`,
`.sidecar/`, `AGENTS.md`) inside each consuming repo.

See [DESIGN.md](DESIGN.md) for the architecture, branch model, and open questions.

## Use it in a repo
```toml
# pyproject.toml — stable channel (floating major tag on main; @0 pre-1.0, @1 after launch)
[dependency-groups]
dev = ["fireball_sidecar_toolkit @ git+https://github.com/fireballenterprise/fireball_sidecar_toolkit@0"]
# dev channel: ...@development
```
```sh
uv run --no-sync invoke sidecar.toolkit.sync      # check _shared/ -> offer upload -> download -> regenerate
uv run --no-sync invoke sidecar.toolkit.download  # clobber _shared/ from the package, regenerate
uv run --no-sync invoke sidecar.toolkit.upload    # open a PR here with local _shared/ changes
uv run --no-sync invoke sidecar.toolkit.check     # read-only drift gate (wire into invoke test / CI)
```
No dependency wanted (non-Python repo): `uvx --from git+https://github.com/fireballenterprise/fireball_sidecar_toolkit sidecar-toolkit download`.

## Consuming-repo contract
| path | rule |
|------|------|
| `_shared/` | clobbered copy of the toolkit's `content/` — never hand-edit |
| `_local/` | this repo's own `instructions/ commands/ skills/` — never synced |
| `.claude/`, `.github/{prompts,instructions,copilot-instructions.md}`, `.clinerules/`, `.opencode/`, `.sidecar/`, `AGENTS.md`, `CLAUDE.md` | generated — never hand-edit |

Fix shared behavior by editing `content/` here, or by editing `_shared/` in a consuming repo and
running `sidecar.toolkit.upload` to open a PR.

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
