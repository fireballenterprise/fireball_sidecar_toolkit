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
ambiguous input — is captured as instructions in `.github/prompts/*.prompt.md`. These prompt files
are the single source of truth every AI tool reads for command *behavior* (see
`prompts.instructions.md` for authoring them). If a decision isn't written down in a `.prompt.md`
file or a standing rule in `.github/instructions/`, an AI enforcing it is not reproducible.

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

**`.github/instructions/` is the one and only source of truth for all AI rules.**

All providers ultimately read from here. Never duplicate rules into provider-specific files — update the instruction files and let providers pick them up.

### Provider Hierarchy

| Priority | Provider | Config files read | How rules flow in |
|----------|----------|-------------------|-------------------|
| 1 (primary) | **GitHub Copilot** | `.github/copilot-instructions.md` + `.github/instructions/*.md` | `copilot-instructions.md` is always loaded and is a thin pointer; `.github/instructions/*.md` files with `applyTo` frontmatter additionally auto-apply natively when their glob matches |
| 2 | **OpenCode** | `AGENTS.md` (repo root) | `AGENTS.md` is a thin pointer; all substance is in `.github/instructions/` |
| 3 | **Claude TUI** | `CLAUDE.md` → `AGENTS.md` | `CLAUDE.md` delegates to `AGENTS.md`, which delegates to `.github/instructions/` |

### File Roles

| File | Role | Contents |
|------|------|----------|
| `.github/instructions/*.md` | **Source of truth** — update here only | All rules, standards, workflow |
| `.github/copilot-instructions.md` | Thin pointer for Copilot, always loaded | One-liner pointing to `index.instructions.md` |
| `AGENTS.md` (root) | Thin pointer for OpenCode / other tools | Slash command quick-ref + links to instruction files |
| `CLAUDE.md` (root) | Thin pointer for Claude TUI | One-liner pointing to `AGENTS.md` |
| `topics/*/AGENTS.md` | Topic-scoped pointer | Topic context + link to root `AGENTS.md` |
| `topics/*/CLAUDE.md` | Topic-scoped pointer for Claude | Points to topic `AGENTS.md` |

### Adding a New Provider

1. Check whether it natively reads `.github/instructions/` — if yes, nothing extra needed.
2. If not, create a thin entrypoint file (e.g. `NEWPROVIDER.md`) that reads:
   > "See `AGENTS.md` for all instructions. `.github/instructions/` is the source of truth."
3. Do **not** copy rules into the new file — always delegate.

### Removing a Provider

Delete its entrypoint file(s) only. `.github/instructions/` and `AGENTS.md` stay untouched.

- Remove OpenCode → delete `.opencode/` dir + `AGENTS.md` (if no other tool needs it)
- Remove Claude → delete `CLAUDE.md` + `.claude/` dir

## Documentation

- `.github/instructions/logic.instructions.md` — AI decision architecture, modules/invoke/AI stack, provider hierarchy (this file)
- `.github/instructions/layout.instructions.md` — repository and directory layout
- `.github/instructions/prompts.instructions.md` — AI custom prompts / slash command standards and templates
- `.github/instructions/tasks.instructions.md` — invoke task runner (plain CLI automation, no AI)
- `.github/instructions/modules.instructions.md` — Python module architecture and layout conventions
- `.github/instructions/tests.instructions.md` — testing requirements and workflow
- `.github/instructions/index.instructions.md` — repository-wide operating rules
