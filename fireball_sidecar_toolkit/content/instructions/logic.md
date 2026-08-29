---
applyTo: "**"
---
# Logic Architecture Instructions

## Core Principle

**All business logic lives in Python, in `modules/`, so it's testable. Everything else is a thin
CLI wrapper around it — and the AI is a decision-making wrapper on top of that CLI, not a fourth
code layer.**

## The Stack

```
modules/*/            All business logic. Reusable, testable. The only place anything
                       deterministic actually happens.
        ↑
        ├── modules/*/route.py   Thin dispatch, reached via slash commands. No logic.
        └── tasks/*.py (invoke)  Thin CLI wrapper too, reached via `invoke <task>`. Used for
                                  CI/CD-style automation (fix, test, sync, setup, upgrade)
                                  rather than interactive slash commands. No logic here either
                                  — see `tasks.instructions.md`.
        ↑
An AI (or a human) calls either CLI — `python -m modules.*.route` or `invoke <task>` — exactly
the way a human operator would from a terminal. Neither CLI knows or cares whether an AI or a
person is driving it.
```

- **Layer: Modules** (`modules/*/`) — ALL business logic, reusable, testable.
- **Layer: CLI wrappers** (`modules/*/route.py` for slash commands, `tasks/*.py` for `invoke`) —
  thin dispatch only, no business logic, no AI-specific behavior. Both are equally "just a CLI":
  deterministic, scriptable, runnable by a human or CI with zero AI involved.
- **Not a layer: the AI** — it's an intelligence/decision-making wrapper *on top of* the CLI
  above, not a layer inside it. It calls `route.py` or `invoke` exactly like a human user would,
  and makes some of the same judgment calls a human operator would (which options to pick, when
  to ask, when to stop). See below for where that judgment is captured.

## AI Is an Automated User, Not a Fourth Layer

The stack above is the entire runtime. An AI tool operates the CLI exactly the way a human would
type it at a terminal — there is no hidden AI-only code path, and no logic lives inside the AI
itself.

**Where the "intelligence" lives.** All dynamic, judgment-based decision-making an AI applies while
running a command — which options to pick, what to ask the user, when to stop, how to interpret
ambiguous input — is captured in the canonical command bodies (`fireball_sidecar_toolkit`'s
`content/commands/`, rendered into `.github/prompts/` and the other provider dirs). Those bodies
are the single source of truth every AI tool reads for command *behavior* (see
`prompts.instructions.md` for authoring them). If a decision isn't written down in a command body
or a standing rule in `.github/instructions/`, an AI enforcing it is not reproducible.

**The reproducibility test.** Before letting an AI make a judgment call inside a command, ask:
*could a human, or a CI script, make the same call by hand — reading the same `.prompt.md` file and
running the same `uv run --no-sync python -m modules.*.route "..."` / `invoke` commands — with zero
AI involved?* If yes, the design is correct: the AI is an automated user of a CLI that already
fully works without it. If no, the missing logic belongs in a prompt file (if it's judgment) or a
Python module (if it's deterministic) — never only in the AI's head.

**Why this matters — provider agnosticism.** Because judgment lives in prompt files and standing
rules live in `.github/instructions/`, no business logic and no decision logic is tied to any
specific AI model or vendor. Adding or swapping a provider (see Provider Hierarchy below) never
requires re-teaching it anything new — it only needs to read the same prompts and instructions and
call the same CLI, exactly like every other provider already does.

## AI Provider Architecture

### Source of Truth

Shared rules, commands, and skills are authored once in **`fireball_sidecar_toolkit`'s `content/`**
(repo-specific ones in this repo's `_local/`). A generator renders them into every provider's
native files. Two kinds of output:

- **Materialised** (the tool reads the text directly): `.github/instructions/*.instructions.md`
  (full body + `applyTo`), `.github/prompts/*.prompt.md`, `.github/skills/*/SKILL.md`, and
  `AGENTS.md` (a generated index of the instruction set).
- **Generated pointers** back to those: `.claude/`, `.clinerules/workflows/`, `.sidecar/`,
  `CLAUDE.md`.

**Never hand-edit a generated provider file.** Edit canonical content (or `_local/`) and run
`invoke sidecar.toolkit.download`; `invoke sidecar.toolkit.check` (inside `invoke test`) fails on
drift.

### Providers

| Provider | Reads | Notes |
|----------|-------|-------|
| **GitHub Copilot** | `.github/copilot-instructions.md` + `.github/instructions/*.md` | the `applyTo` glob auto-applies a rule file natively when it matches |
| **Claude Code** | `CLAUDE.md` → `AGENTS.md` → `.github/instructions/`; `.claude/commands/` + `.claude/skills/` | |
| **Fireball Sidecar** | `AGENTS.md` + `.github/instructions/` (honouring `applyTo`) + `.github/prompts/`; interim `.sidecar/` pointer stubs | |
| **Codex / other AGENTS.md tools** | `AGENTS.md` → `.github/instructions/` | |

### Adding or removing a provider

Add or remove a **renderer** in `fireball_sidecar_toolkit/renderers/` — not a hand-maintained
pointer file. The generator owns every provider dir.

## Documentation

- `logic.instructions.md` — this file (stack + provider architecture)
- `prompts.instructions.md` — canonical command authoring
- `tasks.instructions.md` — invoke task runner (plain CLI automation, no AI)
- `modules.instructions.md` — Python module architecture and layout conventions
- `tests.instructions.md` — testing requirements and workflow
- `index.instructions.md` — repository-wide operating rules
