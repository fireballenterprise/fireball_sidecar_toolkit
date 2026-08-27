---
applyTo: "modules/**"
---
# Python Modules Instructions

## Architecture

See `.github/instructions/logic.instructions.md` for the Core Principle and The Stack — commands
and invoke tasks are both thin CLI wrappers, all business logic lives here in `modules/`.

## Module Layout Consistency

Every module folder under `modules/` follows the same shape so any module is navigable without
reading its source first:

- **`route.py`** — required in every module reachable from a slash command; dispatch only (see
  `prompts.instructions.md` for the router template). Sync-only modules with no slash command
  (e.g. `ollama/`) may omit it.
- **`README.md`** — required in every module folder; documents the module's purpose and what each
  file does.
- **One file per verb/subcommand** — e.g. `chat/` has `start.py`, `end.py`, `list.py`, `resume.py`,
  not one large file. The filename matches the CLI subcommand name exactly
  (`financials/update_card_limit.py` → `/financials update_card_limit`).
- **Naming** — module directory names are lowercase `snake_case` nouns matching the domain/tool
  they wrap (`financials`, `opencode`, `topic`) — never mixed case or a `_module` suffix.
- **Sync-only modules** (`hermes/`, `opencode/`) are the lightweight exception: just `sync.py`,
  plus `route.py` only where a slash command exists.
- **`common/`** is the only module importable from every other module — it holds no domain logic
  of its own, only shared plumbing.

## Mandatory Standards

### Named Options Only (NO positional arguments)

```python
# ✅ CORRECT
@cli.command()
@cli.option("--title", default=None, help="Title for the chat")
def main(title: str | None = None):
    pass


# ❌ WRONG — never use positional arguments
def main(title):
    pass
```

### Path Resolution

Always use `modules/common/properties.py` — never hardcode paths:

```python
from ..common.properties import get_repo_local, get_screenshots_location

repo_root = get_repo_local()
screenshots = get_screenshots_location()
```

### Inter-Module Import Rules

- `common/` utilities: importable from any module
- No cross-imports between domain modules (`chat/`, `topic/`, `repo/`, `financials/`, etc.)
- If truly shared: move to `common/`

## Code Quality

All Python changes must achieve 10/10 before any commit. See `.github/instructions/tests.instructions.md`.

**Fix issues. Never disable linter warnings without user approval.**

## templates.py Change Rule

`modules/topic/templates.py` is the single source of truth for all topic instruction file content (OPENCODE.md). It drives what gets generated when `/topic init` or `/topic update` runs.

**When you modify `templates.py`:**
1. Run fix + test as usual (10/10 required)
2. **Ask the user**: "Should I run `/topic update` to regenerate all topic AGENTS.md files with the new template?"
3. Also **check whether `AGENTS.md` (repo root) needs manual sync** — root AGENTS.md is hand-maintained and may need the same rule added if the template change reflects a new policy

## Common CLI Option Patterns

```python
# Optional string
@cli.option("--title", default=None, help="Title for the chat")

# Required string
@cli.option("--path", required=True, help="Path to topic")

# Boolean flag
@cli.option("--yes", "-y", is_flag=True, help="Skip confirmation")

# Integer with default
@cli.option("--count", default=20, help="Number of items")

# Choice from list
@cli.option("--sort", type=cli.Choice(["newest", "oldest"]), default="newest")

# Path that must exist
@cli.option("--file", type=cli.Path(exists=True), help="Input file")
```

### What `modules.common.cli` Provides

- **Automatic parsing** — Converts CLI strings to Python types
- **Help generation** — Auto-generates `--help` documentation
- **Type validation** — Ensures correct types (string, int, bool, Path)
- **Default values** — Handles optional parameters elegantly
- **Error handling** — User-friendly error messages

## Module File Reference

```
modules/
├── chat/
│   ├── active.py       # Active chat state (active.yml)
│   ├── end.py
│   ├── list.py
│   ├── resume.py
│   ├── route.py        # /chat routing
│   └── start.py
├── claude/
│   └── route.py        # /claude routing (proxies to claude CLI)
├── common/
│   ├── cli.py            # Click-like CLI wrapper
│   ├── invoke_runner.py
│   ├── properties.py     # Central properties.yml loader — use for all paths
│   ├── route_utils.py    # find_repo_root, build_env
│   └── utils.py
├── employment/
│   ├── docker/           # Reactive Resume Docker Compose service (compose.yml + gitignored .env/data)
│   ├── resume.py         # /resume create|update|sync|setup|clean — see module README
│   └── route.py          # /resume routing (and future employment-topic commands)
├── financials/
│   ├── route.py
│   └── update_card_limit.py
├── hermes/
│   └── sync.py         # Syncs ~/.hermes/ config + SKILL.md from .github/prompts/
├── ollama/
│   ├── helpers.py      # Shared helpers (pull_model via Ollama REST API)
│   ├── install.py      # Install Ollama + local coding LLM on Apple Silicon
│   ├── list.py         # List installed and available models
│   ├── status.py       # Show service + running-model status
│   ├── uninstall.py    # Uninstall Ollama + remove all models
│   └── update.py       # Update binary + models + cleanup orphaned blobs
├── opencode/
│   └── sync.py         # Syncs .opencode/command/ from .github/prompts/
├── repo/
│   ├── cleanup.py
│   ├── pull.py
│   ├── push.py
│   ├── rebase.py
│   ├── route.py
│   ├── set_screenshots.py
│   ├── squash.py
│   └── view_screenshot.py
├── setup/
│   ├── properties.py   # Creates properties.yml (inv setup.properties); no-op if it exists
│   └── templates/properties/*.yml  # Tiered template fragments merged into a fresh properties.yml
├── template/
│   ├── pull.py          # /template pull — resolve template_ai_vault local path
│   ├── push.py          # /template push — diff/apply/create-pr against template_ai_vault
│   ├── resolve.py        # Shared local-path-or-clone resolution
│   ├── route.py          # /template routing
│   └── scope.py          # Push include/exclude scope rules
├── topic/
│   ├── active.py       # Active topic state (active_topic.yml)
│   ├── init.py
│   ├── list.py
│   ├── new.py
│   ├── route.py        # /topic routing
│   ├── switch.py
│   ├── templates.py    # Single source of truth for OPENCODE.md content
│   │                   # ⚠️  See topics.instructions.md → "templates.py Change Rule" when modifying this file.
│   ├── update.py
│   └── update_list.py
└── versioning/
    ├── libs.py          # pyproject.toml deps vs. latest release
    ├── python.py        # Pinned Python version vs. latest release
    ├── upgrade.py       # Actual install/sync (used by /upgrade)
    └── workflows.py     # .github/workflows/ action refs vs. latest tag
```

`/update` and `/upgrade` route through `tasks/versioning.py` (the invoke `ver` collection, see
`tasks.instructions.md`), not a `route.py` — there's no per-slash-command router module for this
one, unlike most other modules.

## AI Tool Sync Modules

`.github/prompts/` is the single source of truth for all slash commands — see
`.github/instructions/logic.instructions.md` for why. Two sync modules generate tool-specific
formats from it:

| Module | Output | Invoke command |
|---|---|---|
| `modules/hermes/sync.py` | `~/.hermes/config.yaml` + `SKILL.md` | `inv hermes.sync` |
| `modules/opencode/sync.py` | `.opencode/command/*.md` | `inv opencode.sync` |

Run `inv ai.sync` to regenerate both at once. Never hand-edit these two output dirs.

`.claude/commands/*.md` and `.clinerules/workflows/*.md` have no sync script — they're
hand-maintained 1:1 mirrors of `.github/prompts/`, verified by `inv tests.check_agents`. See
`.github/instructions/prompts.instructions.md`.

## Module Template

```python
"""
Module description.

Usage:
    uv run --no-sync python -m modules.<group>.<name> [--option value]
"""

from modules.common import cli
from modules.common.properties import get_repo_local


@cli.command()
@cli.option("--argument", default=None, help="Description of argument")
def main(argument: str | None = None) -> None:
    """One-line summary of what this module does."""
    repo_root = get_repo_local()
    cli.echo(f"Repo root: {repo_root}")
    # Business logic here


if __name__ == "__main__":
    main()
```
