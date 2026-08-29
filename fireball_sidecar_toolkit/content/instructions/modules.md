---
description: "Use when creating, editing, or navigating Python code under modules/ — folder shape, mandatory CLI standards, path resolution, and the module template."
applyTo: "modules/**"
---
# Python Modules Instructions
All business logic lives here — slash commands and invoke tasks are thin CLI wrappers around it
(see `.ai/shared/instructions/logic.md`). Python style, ordering, and comment rules are in
`.ai/shared/instructions/python.md`; the 10/10 test gate is in `.ai/shared/instructions/tests.md`.

## Module Layout Consistency
Every folder under `modules/` follows the same shape so any module is navigable without reading
its source first:

- **`route.py`** — required in every module reachable from a slash command; dispatch only (router
  template below). Modules with no slash command may omit it.
- **`README.md`** — required in every module folder; documents the module's purpose and each file.
- **One file per verb/subcommand** — `chat/` has `start.py`, `end.py`, `list.py`, `resume.py`, not
  one large file. The filename matches the CLI subcommand exactly
  (`screenshots/configure.py` → `/screenshots configure`).
- **Naming** — directory names are lowercase `snake_case` nouns matching the domain/tool wrapped
  (`chat`, `repo`, `topic`, `versioning`) — never mixed case, never a `_module` suffix.
- **`common/`** is the only module importable from every other module — shared plumbing only, no
  domain logic.

## Mandatory Standards
### Named options only (no positional arguments)
```python
# ✅ CORRECT
@cli.command()
@cli.option("--title", default=None, help="Title for the chat")
def main(title: str | None = None):
    pass


# ❌ WRONG
def main(title):
    pass
```

### Path resolution
Always use `modules/common/properties.py` — never hardcode paths:
```python
from ..common.properties import get_repo_local, get_screenshots_location

repo_root = get_repo_local()
```

### Inter-module imports
- `common/` utilities: importable from any module
- No cross-imports between domain modules (`chat/`, `topic/`, `repo/`, …) — if truly shared, move it to `common/`

## templates.py Change Rule
`modules/topic/templates.py` is the single source of truth for each topic's generated `AGENTS.md`
/ `CLAUDE.md`. When you modify it, follow the **templates.py Change Rule** in
`.ai/shared/instructions/topics.md` (fix + test, ask about `/topic update`).

## Common CLI Option Patterns
```python
@cli.option("--title", default=None, help="...")            # optional string
@cli.option("--path", required=True, help="...")             # required string
@cli.option("--yes", "-y", is_flag=True, help="...")         # boolean flag
@cli.option("--count", default=20, help="...")               # int with default
@cli.option("--sort", type=cli.Choice(["newest", "oldest"]), default="newest")
@cli.option("--file", type=cli.Path(exists=True), help="...")
```
`modules.common.cli` handles parsing, `--help` generation, type validation, defaults, and
user-friendly errors.

## Router Template
```python
# modules/<module>/route.py — argument dispatch only
import shlex, subprocess, sys
from modules.common.route_utils import build_env, find_repo_root

_SUBCOMMAND_MODULES = {"start": "modules.<module>.start", "end": "modules.<module>.end"}


def main() -> int:
    args = shlex.split(sys.argv[1] if len(sys.argv) > 1 else "")
    module = _SUBCOMMAND_MODULES.get(args[0]) if args else None
    if module is None:
        sys.stderr.write("Unknown subcommand\n")
        return 1
    repo_root = find_repo_root()
    cmd = [sys.executable, "-m", module, *args[1:]]
    return subprocess.run(cmd, cwd=repo_root, env=build_env(repo_root), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
```

## AI Provider Files
Commands, instructions, and skills are authored in `.ai/shared/` (via `fireball_sidecar_toolkit`'s
`content/`) or this repo's `.ai/local/`, and rendered as pointer stubs into every provider dir by
`invoke sidecar.toolkit.download`. There are no per-repo sync modules —
`invoke sidecar.toolkit.check` (inside `invoke test`) is the drift gate. See
`.ai/shared/instructions/ai_commands.md`.

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


if __name__ == "__main__":
    main()
```
