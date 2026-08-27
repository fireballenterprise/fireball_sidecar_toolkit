# ai_devkit
[![Tests](https://github.com/LevonBecker/ai_devkit/actions/workflows/tests.yml/badge.svg)](https://github.com/LevonBecker/ai_devkit/actions/workflows/tests.yml)

Single source of truth for Levon's shared AI-agent tooling. Canonical slash commands, agent
instructions, and skills live here as tool-neutral markdown under `content/`; a generator renders
them into every AI tool's native format (`.claude/`, `.github/prompts/`, `.github/instructions/`,
`.clinerules/`, `.opencode/`, `.sidecar/`, `AGENTS.md`) inside each consuming repo.

See [DESIGN.md](DESIGN.md) for the architecture and open questions.

## Use it in a repo
```toml
# pyproject.toml
[dependency-groups]
dev = ["ai-devkit @ git+https://github.com/levonbecker/ai_devkit@1"]
```
```sh
uv run --no-sync invoke devkit.sync     # check _shared/ -> offer upload -> download -> regenerate
uv run --no-sync invoke devkit.download # clobber _shared/ from the package, regenerate
uv run --no-sync invoke devkit.upload   # open a PR here with local _shared/ changes
uv run --no-sync invoke devkit.check    # read-only drift gate (wire into invoke test / CI)
```
No dependency wanted (e.g. a non-Python repo): `uvx --from git+https://github.com/levonbecker/ai_devkit devkit download`.

## Consuming-repo contract
| path | rule |
|------|------|
| `_shared/` | clobbered copy of `content/` — never hand-edit |
| `_local/` | this repo's own `instructions/ commands/ skills/` — never synced |
| `.claude/`, `.github/{prompts,instructions,copilot-instructions.md}`, `.clinerules/`, `.opencode/`, `.sidecar/`, `AGENTS.md`, `CLAUDE.md` | generated — never hand-edit |

Fix shared behavior by editing `content/` here, or by editing `_shared/` in a consuming repo and
running `devkit upload` to open a PR.

## Repo layout
```
content/
  instructions/*.md   canonical agent rules (frontmatter: description, applyTo)
  commands/*.md        canonical slash-command specs (name, description, argument-hint; body has the !`...` exec line)
  skills/<name>/SKILL.md
modules/devkit/         parser (content.py), orchestrator (render.py), primitives
  renderers/            one per AI tool
tasks/devkit/           invoke wrappers
```

## Development
```sh
./setup.sh
uv run --no-sync invoke fix
uv run --no-sync invoke test
```
