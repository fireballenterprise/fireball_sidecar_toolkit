---
name: push
description: Push changes to git remote — invoke fix, invoke test, then commit and push. `all` runs the full push in every family repo.
argument-hint: "[all]"
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.repo.route "push $ARGUMENTS"`

Bare `/push` pushes the current repo. `/push all` runs the real `/push` (invoke fix + invoke test
+ commit + push) in every repo in `properties.yml`'s `repos:` family — same as `/repo push all`.
Confirm the repo list first, and never skip a repo's tests.
