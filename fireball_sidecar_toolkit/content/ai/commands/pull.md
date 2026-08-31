---
name: pull
description: Pull updates from git remote — stash, pull with rebase, restore stash. `all` pulls every repo in the family.
argument-hint: "[all]"
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.repo.route "pull $ARGUMENTS"`

Bare `/pull` rebases the current branch. `/pull all` switches every repo in `properties.yml`'s
`repos:` family to its verified default branch and `pull --ff-only`s each — same as `/repo pull all`.
