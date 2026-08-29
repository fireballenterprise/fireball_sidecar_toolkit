---
description: "Use when creating or editing a canonical skill file — .ai/shared|local/skills/<name>.md and the SKILL.md stubs the generator renders from it."
applyTo: ".ai/shared/skills/**,.ai/local/skills/**,.claude/skills/**,.github/skills/**,.sidecar/skills/**"
---
# AI Skills Instructions
## Canonical skill file (`.ai/shared/skills/<name>.md`)
Flat, one file per skill (repo-specific ones in `.ai/local/skills/<name>.md`). Frontmatter:

```yaml
---
name: command_name
description: Use for ... . Equivalent to /command_name.
hints:            # optional — extra natural-language trigger phrases
  - punch it
---
```

Every canonical command (`.ai/shared/commands/<slug>.md`) has a matching
`.ai/shared/skills/<slug>.md`. The body is a **short pointer, not a mirror** — point at
`.ai/shared/commands/<slug>.md` and summarize when the skill fires; never duplicate the command
body.

## Rendered stubs (generated — never hand-edit)
| Location | Tool | Notes |
|---|---|---|
| `.claude/skills/<name>/SKILL.md` | Claude Code | rendered for every skill; body is a pointer at `.ai/shared|local/skills/<name>.md` |
| `.github/skills/<name>/SKILL.md` | GitHub Copilot (VS Code) | same shape; discovery is driven by `description` + `hints` |
| `.sidecar/skills/<name>.md` | Fireball Sidecar | flat pointer stub |

The `<name>/SKILL.md` directory shape is a *rendered artifact* Claude Code / Copilot require — the
canonical source is always the flat `.ai/…/skills/<name>.md`.

## Trigger phrases
Add a `hints:` entry (or spell the phrase out in `description`) for any trigger beyond the slash
name — e.g. `ship-it` also responds to "punch it" / "ship it". That is Copilot's discovery
surface; an implied phrase is not discovered.

Uses the Agent Skills open spec, but treat it as Claude Code-specific until other targeted tools
adopt it — hence `.claude/` rather than a vendor-neutral `.agents/`.

## Related
- `.ai/shared/instructions/ai_commands.md` — canonical command / instruction authoring
- `.ai/shared/instructions/logic.md` — overall AI/logic architecture
