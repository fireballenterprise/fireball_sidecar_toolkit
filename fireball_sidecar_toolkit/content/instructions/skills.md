---
applyTo: ".claude/skills/**,.github/skills/**"
---
# Skills Instructions

## Two Skill Locations
This repo has two separate `SKILL.md`-based directories, serving different purposes:

| Location | Tool | Purpose | Sync requirement |
|----------|------|---------|-------------------|
| `.claude/skills/<name>/SKILL.md` | Claude Code | Auto-discovered mirror of every `.github/prompts/*.prompt.md` command | Required 1:1 (see `prompts.instructions.md`) |
| `.github/skills/<name>/SKILL.md` | GitHub Copilot (VS Code) | Optional, on-demand skill for a specific workflow | None — add only where useful, no mirror required |

## Claude Code Skills (.claude/skills/*/SKILL.md)
```yaml
---
name: command_name
description: Use for ... . Equivalent to /command_name.
---
```
One directory per command, named to match (`.claude/skills/push/SKILL.md` for `/push`). The body
is a **pointer, not a mirror** — point at the `.github/prompts/*.prompt.md` file as source of truth
and summarize the underlying command, rather than duplicating the full prompt body. See any
existing `.claude/skills/*/SKILL.md` for the pattern.

This uses the Agent Skills format (published as an open spec, in principle implementable by any
tool), but treat it here as **Claude Code-specific** until other tools this repo targets
demonstrably adopt it — hence living under `.claude/` rather than a vendor-neutral `.agents/`.

Every canonical command in `fireball_sidecar_toolkit`'s `content/commands/` has a matching
`content/skills/<slug>/SKILL.md`; the generator copies the skill dir into `.claude/skills/` and
`.github/skills/` and renders a `.sidecar/skills/` pointer. See `prompts.instructions.md`.

## GitHub Copilot Skills (.github/skills/*/SKILL.md)
```yaml
---
name: command_name
description: Use for ... . Equivalent to /command_name. Also triggered by "<phrase>", ...
---
```
Same frontmatter shape as the Claude version above, and the body is likewise a pointer at the
`.github/prompts/*.prompt.md` file, not a mirror of it.

Unlike `.claude/skills/`, this directory is **not required for every command** — add one only when
a command benefits from natural-language trigger phrases beyond its slash-command name. For
example, `ship-it` responds to "punch it", "punch it chewy", or "ship it" in addition to
`/ship-it` (see `.github/skills/ship-it/SKILL.md`).

`description` is the discovery surface GitHub Copilot uses to decide whether to invoke a skill —
any trigger phrase the skill should respond to must be spelled out in `description`, not just
implied by the skill's name.

## Related Instructions
- `prompts.instructions.md` — slash command / prompt file conventions and the synced command dirs
- `logic.instructions.md` — overall AI/logic architecture
