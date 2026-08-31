---
description: "Use when authoring a canonical slash command or instruction file (.ai/toolkit/ via the toolkit, or a repo's .ai/<repo>/) — the generator model, required frontmatter, and the thin-wrapper body."
applyTo: ".ai/*/commands/**,.ai/*/instructions/**,.claude/commands/**,.clinerules/workflows/**,.github/prompts/**,.sidecar/commands/**"
---
# AI Commands Instructions
Standards for the slash commands / custom prompts. **Commands are authored once** in
`fireball_sidecar_toolkit`'s `content/commands/*.md` (mirrored into each consuming repo as
`.ai/toolkit/commands/`; repo-specific ones in `.ai/<repo>/commands/`) and a generator renders one
pointer stub per tool. **Never hand-edit a generated provider file** — edit the `.ai/` source and
re-run `invoke sidecar.toolkit.apply`.

## Architecture
Commands are the AI-facing entrypoint layer described in `.ai/toolkit/instructions/logic.md` (Core Principle +
The Stack) — thin wrappers only, no business logic. See that file for why command bodies are the
AI's decision-capture layer, and how this differs from `.ai/toolkit/instructions/tasks.md`'s plain CLI
automation.

## Canonical command file (`.ai/toolkit/commands/<slug>.md`)
```yaml
---
name: <slug>
description: One line — what it does + when to use it
argument-hint: arg1 | arg2 [optional]      # or "no arguments required"
agent: agent
allowed-tools:                             # optional — only when the derived default is wrong
  - Bash(gh pr create *)
---

!`uv run --no-sync python -m modules.toolkit.<module>.route "$ARGUMENTS"`

<optional extra guidance for the agent — kept verbatim in every rendered view>
```

The `!` prefix runs bash; `$ARGUMENTS` receives everything after the command name. A command with
no `!` line is prose-only (the agent just follows the body).

## What the generator emits per tool
Every generated file is a **pointer stub**: provider frontmatter + one line
`Source of truth: .ai/toolkit/commands/<slug>.md` (or `.ai/<repo>/…`). No body is inlined.

| Tool | File | Frontmatter it still carries |
|------|------|------|
| GitHub Copilot | `.github/prompts/<slug>.prompt.md` | `name` + `description` + `argument-hint` + `agent` |
| Claude Code | `.claude/commands/<slug>.md` | `description` + `subtask: false` + `agent: general` + `slash_command: /<slug>` + a derived `allowed-tools` glob |
| Cline | `.clinerules/workflows/<slug>.md` | none (body-only file) |
| Fireball Sidecar | `.sidecar/commands/<slug>.md` | `name` + `description` + `argument-hint` + `agent` |

`allowed-tools` is still derived from the canonical `!` exec line (`uv run --no-sync …` →
`Bash(uv run --no-sync *)`, `AWS_PROFILE=X uv run …` → that plus the bare glob, `./setup.sh` →
`Bash(./setup.sh)`). Override it in canonical frontmatter only when that default is wrong.

## Creating a new command
1. Python module — `modules/<module>/<verb>.py` (ALL logic here) + `modules/<module>/route.py`
   (argument dispatch only). See `.ai/toolkit/instructions/modules.md` for the router template.
2. `.ai/toolkit/commands/<slug>.md` — the thin wrapper above.
3. `.ai/toolkit/skills/<slug>.md` — the matching skill (see `.ai/toolkit/instructions/ai_skills.md`).
4. `uv run --no-sync invoke sidecar.toolkit.apply` to regenerate, then `invoke fix && invoke
   test` (must be 10/10 for `.py` changes).

## Authoring instruction files (`.ai/toolkit/instructions/<slug>.md`)
- One file per concern — the generated `AGENTS.md` index lists them all, derived from the bundle
- Always include a `description` in YAML frontmatter using the "Use when..." pattern
- Use an `applyTo` glob only when the instruction is relevant to a specific file type or directory
  (`**/*.py`, `**/*.csv`, `.github/workflows/**`); omit it (or `**`) for repo-wide rules
- Keep instructions actionable and example-driven — prefer short code blocks over prose
- No standalone `---` dividers in the body — see `.ai/toolkit/instructions/markdown.md`

## uv --no-sync flag
Every `uv run` call in a command MUST use `--no-sync`:

```
✅ uv run --no-sync python -m modules.toolkit.chat.route "$ARGUMENTS"
❌ uv run python -m modules.toolkit.chat.route "$ARGUMENTS"
```

## Cache restart requirement
AI tools cache command files at startup. After an `apply` regenerates them, restart the AI tool
before testing.

## How a slash command routes
```
User: /chat resume wire_tunnels
  ↓  AI tool reads the rendered command file for its own format
  ↓  body executes: uv run --no-sync python -m modules.toolkit.chat.route "resume wire_tunnels"
  ↓  modules/toolkit/chat/route.py dispatches → modules.toolkit.chat.resume --pattern="wire_tunnels"
  ↓  the Python function receives pattern="wire_tunnels"
```
