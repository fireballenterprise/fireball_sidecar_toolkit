---
name: upgrade
description: Upgrade Python and/or Dependencies
argument-hint: [python | libs]
agent: agent
---

# upgrade - Upgrade Python and/or Dependencies

Executes upgrades to Python and/or package dependencies after you've reviewed changes via `/update`.

## Usage

Upgrade everything (interactive):
!`uv run --no-sync invoke upgrade`

Upgrade only Python:
!`uv run --no-sync invoke upgrade.python`

Upgrade only libs:
!`uv run --no-sync invoke upgrade.libs`

Sync dependencies without checking for updates:
!`uv run --no-sync invoke upgrade.sync`

## Description

The upgrade command performs actual installations and syncs:
- Downloads and installs new Python versions (if updated)
- Rebuilds virtual environment (if Python changed)
- Runs `uv sync --upgrade` to install updated dependencies

## Workflow

Best practice:
1. Run `/update` to review and update config files
2. Check `git diff` to see what changed
3. If satisfied, run `/upgrade` to execute the upgrades
4. If not satisfied, run `git restore` and adjust

## Examples

```bash
# Full workflow
/update                    # Review and update all configs
git diff                    # Review changes
/upgrade                    # Execute upgrades

# Python-only workflow
/update python             # Review and update Python configs
git diff                    # Review changes
/upgrade python             # Execute Python upgrade

# Libs-only workflow
/update libs               # Review and update lib versions in pyproject.toml
git diff                    # Review changes
/upgrade libs               # Execute libs upgrade
```

## Exit Codes

- 0: Success (upgrades completed or nothing needed)
- 1: Error occurred
- 2: Cancelled by user
