---
description: "Use when creating or editing a SKILL.md — the Claude Code skill mirror and the optional GitHub Copilot skills."
applyTo: ".claude/skills/**,.github/skills/**,.sidecar/skills/**"
---
# AI Skills Instructions

## Two Skill Locations
| Location | Tool | Purpose | Mirror requirement |
|---|---|---|---|
| `.claude/skills/<name>/SKILL.md` | Claude Code | Auto-discovered skill for every command | Required 1:1 — the drift check |
| `.github/skills/<name>/SKILL.md` | GitHub Copilot (VS Code) | Optional, on-demand skill with natural-language triggers | None — add only where useful |

Every canonical command in `fireball_sidecar_toolkit`'s `content/commands/` has a matching
`content/skills/<slug>/SKILL.md`; the generator copies the skill dir into `.claude/skills/` and
`.github/skills/` and renders a `.sidecar/skills/` pointer.

## Claude Code Skills (`.claude/skills/*/SKILL.md`)
```yaml
---
name: command_name
description: Use for ... . Equivalent to /command_name.
---
```
One directory per command, named to match (`.claude/skills/push/SKILL.md` for `/push`). The body
is a **pointer, not a mirror** — point at the `.github/prompts/*.prompt.md` source of truth and
summarize the command, don't duplicate the prompt body. Required for every command (see
`ai_commands.instructions.md`).

Uses the Agent Skills open spec, but treat it as Claude Code-specific here until other targeted
tools adopt it — hence `.claude/` rather than a vendor-neutral `.agents/`.

## GitHub Copilot Skills (`.github/skills/*/SKILL.md`)
Same frontmatter shape; body is likewise a pointer at the `.github/prompts/*.prompt.md` file.
**Not** required for every command — add one only when a command benefits from trigger phrases
beyond its slash name (e.g. `ship-it` also responds to "punch it" / "ship it"). Every trigger
phrase must be spelled out in `description` — that's Copilot's discovery surface — not just implied
by the name.

## Related
- `ai_commands.instructions.md` — canonical command / instruction authoring
- `logic.instructions.md` — overall AI/logic architecture
