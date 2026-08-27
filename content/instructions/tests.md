---
applyTo: "**/*.py,**/*.yml,**/*.yaml"
---
# Testing Instructions

## Golden Rule

**IF YOU CHANGE `.py`, `.yml`, or `.yaml` FILES — YOU MUST GET 10/10 ON TESTS.**

No exceptions. No shortcuts.

## Workflow

```bash
# 1. Auto-fix first (ALWAYS do this before testing)
uv run --no-sync invoke fix

# 2. Run tests
uv run --no-sync invoke test
# Required: 10/10 score, exit code 0
```

## Canonical Commands (Use These Exactly)

```bash
# Full fix + full test
uv run --no-sync invoke fix
uv run --no-sync invoke test

# Targeted test tasks
uv run --no-sync invoke tests.actionlint
uv run --no-sync invoke tests.pylint
uv run --no-sync invoke tests.rufflint
uv run --no-sync invoke tests.yamllint

# Targeted formatting/fix tasks
uv run --no-sync invoke ruff.fix
uv run --no-sync invoke ruff.format
```

Do not run `uv run invoke ...` without `--no-sync`.

## When to Run Tests

Run tests if you modified:
- `*.py` — any Python file (pylint + ruff)
- `*.yml` or `*.yaml` — any YAML file (yamllint)
- `.github/workflows/*.yml` — GitHub Actions (actionlint + yamllint)

Skip tests for: `*.md`, config files, `*.toml`, `*.json`

## What Gets Tested

1. **actionlint** — GitHub Actions workflow validation
2. **pylint** — Python code quality
3. **ruff** — Python linting and formatting
4. **yamllint** — YAML file validation

## Fix Issues — Never Disable Warnings

```python
# ❌ WRONG — never do this without asking user first
except Exception:  # pylint: disable=broad-exception-caught
    pass

# ✅ CORRECT — catch specific exceptions
except (ValueError, KeyError) as e:
    cli.echo(f"Error: {e}")
```

If an issue is too complex to fix:
1. Try to fix it properly first
2. Ask the user — explain what the linter says and what you've tried
3. Wait for user approval before adding any exclusion
