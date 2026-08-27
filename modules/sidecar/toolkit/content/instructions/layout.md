---
applyTo: "**"
---
# Layout Instructions

Where things physically live. For *why* the runtime is shaped this way, see
`.github/instructions/logic.instructions.md`.

## Active State Files

| File | Location | Purpose |
|------|----------|---------|
| `active.yml` | `topics/<path>/` | Tracks active chat in a topic |
| `active_topic.yml` | repo root | Tracks currently active topic |

Both are git-ignored.

## Repository Boundaries

- **NEVER** write files outside the repository root
- Repo root is defined in `properties.yml` under `repo.local`
- Use `modules/common/properties.py` for all path resolution

## Multi-Tool Command Directory Layout

```
.opencode/command/     # OpenCode slash commands
.claude/commands/      # Claude Code slash commands
.clinerules/workflows/ # Cline workflows
.github/prompts/       # GitHub Copilot prompt files
```

All four dirs contain equivalent commands — keep them in sync when adding new commands. All four
are generated from `.github/prompts/*.prompt.md`, the source of truth (see
`logic.instructions.md`); never hand-edit the generated dirs.

## Top-Level Repository Structure

```
ai_vault/
├── modules/       # ALL business logic (Python) — see modules.instructions.md
├── tasks/         # invoke task definitions — see tasks.instructions.md
├── topics/        # research/business content — see topics.instructions.md
├── screenshots/   # single shared screenshots folder — see screenshots.instructions.md
├── .github/
│   ├── copilot-instructions.md  # always-loaded thin pointer to index.instructions.md
│   ├── instructions/            # source of truth for all AI rules (this directory)
│   └── prompts/                 # source of truth for all slash commands
├── .claude/commands/, .clinerules/workflows/, .opencode/command/  # generated command dirs
└── properties.yml     # central config (repo paths, template repo, repos/lineage map, business config), committed here (gitignored only in template_* repos)
```

See `docs/architecture.md` for the full module-by-module tree.

## The template_ai_vault Relationship

This repo pulls shared, generic tooling updates from — and can push new generic improvements back
to — a separate template repo, `template_ai_vault`, via `/template` (`modules/template/`).
Configured in `properties.yml` under `template.local` / `template.remote`. Only generic,
non-business content is exchanged (see `modules/template/scope.py` for the exact include/exclude
rules) — this repo's own business-specific content (`topics/`, the `financials`/`update_card_limit`
skills, `properties.yml` itself) is never part of that sync in either direction.

## Documentation

- `.github/instructions/layout.instructions.md` — directory layout conventions (this file)
- `.github/instructions/logic.instructions.md` — decision-making architecture and provider hierarchy
- `.github/instructions/modules.instructions.md` — Python module internal layout conventions
- `.github/instructions/index.instructions.md` — repository-wide operating rules
