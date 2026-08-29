---
description: "Use when editing GitHub Actions workflows or composite actions — naming, layout, the invoke-driven job pattern, action-ref pinning, and actionlint."
applyTo: ".github/workflows/**,.github/actions/**"
---
# GitHub Actions Instructions

## Layout
```
.github/
├── workflows/        # top-level workflows
└── actions/          # local composite actions, one dir per action
```

## Conventions
- **File names**: lowercase `snake_case` (`tests.yml`); composite-action dirs likewise
- **YAML**: passes `yamllint` — start with `---`; also validated by `actionlint`
- **`name:` / `run-name:`**: `name:` is a short Title Case label; `run-name:` includes the branch,
  e.g. `"Tests (${{ github.head_ref || github.ref_name }})"`
- **Triggers**: test workflows run on `pull_request` to the default branch
- **One concern per job**: a separate job per check (actionlint, pylint, pytest, ruff, yamllint, …)
  so failures are isolated in the PR checks UI

## Job Pattern
Every job is the same three steps — checkout, setup, run one invoke task:
```yaml
steps:
  - uses: actions/checkout@v7
  - uses: ./.github/actions/cicd_setup     # installs uv + .venv
  - run: |
      source .venv/bin/activate
      invoke debug.env
      invoke tests.<check>
```
The actual check logic lives in `tasks/tests/*.py`, never inline in the workflow — same
thin-wrapper rule as everywhere else (`logic.instructions.md`).

## Action-Ref Pinning
`uses: owner/repo@vN` refs are pinned to a **major** tag (`actions/checkout@v7`). `invoke
ver.workflows` compares each ref against the latest major tag on GitHub and rewrites the pin; run
`invoke tests.actionlint` afterward. See `versioning.instructions.md`.

## Before Committing
`.yml` changes require `uv run --no-sync invoke fix` + `test` at 10/10 — `test` runs both
`actionlint` and `yamllint` (`tests.instructions.md`).
