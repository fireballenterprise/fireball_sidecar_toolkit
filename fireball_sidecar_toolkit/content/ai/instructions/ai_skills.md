---
description: "Use when creating or editing a canonical skill file — .ai/toolkit/ + .ai/<repo>/skills/<name>.md and the SKILL.md stubs the generator renders from it."
applyTo: ".ai/*/skills/**,.claude/skills/**,.github/skills/**,.sidecar/skills/**"
---
# AI Skills Instructions
## Canonical skill file (`.ai/toolkit/skills/<name>.md`)
A canonical skill is a **header only — no body**. Flat, one file per skill (repo-specific ones in
`.ai/<repo>/skills/<name>.md`):

```yaml
---
name: command_name
description: Use for ... . Equivalent to /command_name.
hints:                 # optional — extra natural-language trigger phrases
  - punch it
instructions:          # repo-relative paths to the rule files this skill pulls in
  - .ai/toolkit/instructions/git.md
commands:              # repo-relative paths to the command files this skill drives
  - .ai/toolkit/commands/command_name.md
---
```

A skill is pure wiring: trigger phrases (`description` + `hints`) plus pointers to the
`instructions` and `commands` that carry the actual "how". Never write prose or bash under the
frontmatter — if a skill needs to explain something, that belongs in one of its `instructions`
files.

- `instructions:` / `commands:` are lists of **repo-relative paths**, written verbatim
  (`.ai/toolkit/…` for toolkit content, `.ai/<repo>/…` for a repo's own).
- Every canonical command (`.ai/toolkit/commands/<slug>.md`) has a matching
  `.ai/toolkit/skills/<slug>.md` whose `commands:` list includes at least itself.

## Rendered stubs (generated — never hand-edit)
| Location | Tool | Body the generator writes |
|---|---|---|
| `.claude/skills/<name>/SKILL.md` | Claude Code | `Source of truth:` pointer + the `instructions`/`commands` paths expanded into a "read and follow" block |
| `.github/skills/<name>/SKILL.md` | GitHub Copilot (VS Code) | same; discovery is driven by `description` + `hints` |
| `.sidecar/skills/<name>.md` | Fireball Sidecar | same, flat file |

The generator **synthesises** that body from the frontmatter path lists — no canonical body text
is inlined (there is none). The `<name>/SKILL.md` directory shape is a rendered artifact Claude
Code / Copilot require; the canonical source is always the flat `.ai/…/skills/<name>.md`.

Claude Code and Copilot only natively interpret `name` + `description` (for discovery) and load
the SKILL.md **body** on trigger — arbitrary frontmatter keys are inert. That is why the renderer
materialises `instructions:` / `commands:` into the body instead of leaving them in YAML.

## Trigger phrases
Add a `hints:` entry (or spell the phrase out in `description`) for any trigger beyond the slash
name — e.g. `ship-it` also responds to "punch it" / "ship it". That is Copilot's discovery
surface; an implied phrase is not discovered.

Uses the Agent Skills open spec, but treat it as Claude Code-specific until other targeted tools
adopt it — hence `.claude/` rather than a vendor-neutral `.agents/`.

## Related
- `.ai/toolkit/instructions/ai_commands.md` — canonical command / instruction authoring
- `.ai/toolkit/instructions/logic.md` — overall AI/logic architecture
