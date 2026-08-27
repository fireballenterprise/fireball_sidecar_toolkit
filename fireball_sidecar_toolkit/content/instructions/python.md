---
description: "Use when writing, editing, or reviewing Python code in this project. Covers Python version, style, module conventions, and ruff/pylint configuration."
applyTo: "**/*.py"
---
# Python Instructions

## Python Version
Target: `>=3.14` (defined in `pyproject.toml`, pinned in `.python-version`)

## Style & Linting
- **Ruff** enforces fast style/lint checks — run `uv run --no-sync invoke tests.rufflint` to check, `uv run --no-sync invoke ruff.fix` to auto-correct
- **Pylint** is scoped to just `no-member` — the one check Ruff can't do (real type inference across installed
  deps to catch attribute/method access that doesn't exist on the inferred type). Everything else Pylint could
  flag is left to Ruff to avoid duplicate linting. Run `uv run --no-sync invoke tests.pylint` (must score 10.00/10
  to pass `invoke test` — see `[tool.pylint.messages_control]` in `pyproject.toml`)
- Run `uv run --no-sync invoke fix` to auto-correct everything Ruff can fix, then format
- Config lives in `pyproject.toml` under `[tool.ruff]` and `[tool.pylint]`
- Disable a rule inline only when necessary, with a comment explaining why:
  ```python
  value = compute()  # noqa: PLR0912 -- justified because ...
  ```

## Module & File Conventions
- Use module-level functions (`def foo():`), not classes, unless state genuinely requires it
- Files under `modules/common/` provide shared helpers (`cli`, `properties`, `utils`)
- Files under `modules/repo/` provide git workflow logic; each exposes a `main()` entry point
- Use type hints on function signatures (`def foo(x: int) -> str:`)
- Prefer `pathlib.Path` over string paths

## Constants
- Module-level constants use `UPPER_SNAKE_CASE` (PEP 8)
- Order them alphabetically within their file — same rule, and same trigger, as the function
  ordering in `.github/instructions/style.instructions.md`'s Alphabetical Ordering section: insert
  a new constant in alphabetical position, and correct existing ordering when you're already
  editing that file for another reason — not a mandate to resort files you aren't touching

## Logging & Output
- Use `modules.common.utils` helpers for all console output — `success()`, `error()`, `warning()`, `info()`
- Do not use `print()` directly in `modules/` code (tasks in `tasks/*.py` may `print()` for section headers)
- `error()` prints to stderr and exits the process — use for unrecoverable failures

## Shell Commands
- Use `subprocess.run([...], cwd=repo_path, check=...)` — always pass a list of args, never `shell=True`
- Never interpolate user input into shell strings

## Example Module Pattern
```python
"""One-line module docstring."""

from ..common import cli as click
from ..common.utils import success


def main() -> None:
    """Entry point for this module."""
    click.echo("Doing the thing...")
    success("Done")


if __name__ == "__main__":
    main()
```
