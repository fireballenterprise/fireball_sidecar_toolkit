---
description: "Use when writing or updating project documentation (README, instruction files, inline comments) or per-topic docs/ user-content files (CSV, dates, etc.)."
applyTo: "**"
---
# Docs File Standards

## Project Documentation
### README Conventions
- Lead with a short one-sentence project description
- Include: Setup, Project Structure, Invoke Tasks, AI Prompts, and Modules sections
- Show invoke commands in fenced `sh` code blocks (`uv run --no-sync invoke ...`)
- Keep it concise — link out rather than duplicating content

### Change Logs (`docs/change_logs/<category>/<name>.md`)
Per-entry markdown change logs, generated from `properties.yml` — not hand-written prose. One
file per entry, newest version at the top. `modules/docs/lib/change_logs.py`'s
`CHANGELOG_CATEGORIES` tuple is empty by default — nothing in this repo's `properties.yml` is
version-tracked in that shape yet. Add a category (e.g. `cloudformation` for CDK stacks, keyed by
construct_id) to that tuple once there's an entry worth logging; everything else in the module
already supports it.

**Source of truth is `properties.yml`**, not the markdown file — each category section has one
entry per name:
```yaml
<category>:
  <name>:
    version: 1.0.0
    latest_changes:
      author: Levon Becker    # git config user.name — modules.common.properties.get_git_author()
      date: 2026-08-11
      description: Initial Release    # comma-separate for multiple bullets: "Added X, Fixed Y"
```
Bumped by hand when the entry changes meaningfully — not automated. **A brand-new entry's first
`description` is always `"Initial Release"`.**

**Rendered entry format** (`modules/docs/lib/change_logs.py`'s `expected_entry_text()`):
```markdown
## 1.0.0 - 2026-08-11 - Levon Becker
* Initial Release
```
`## <version> - <date> - <author>` heading, one `* ` bullet per comma-separated `description`
item, blank line, next-newest entry below. No H1 title in the file — the first line is always a
`##` entry heading.

**Sync mechanism** — `modules/docs/lib/change_logs.py`:
- `check_each_log(update=True)` — prepends any missing entry (idempotent; a current entry is a
  no-op). Backs `invoke docs.update-changelogs`, which also runs as part of `invoke fix`
- `check_each_log(update=False)` — read-only; raises `ValueError` on the first stale entry instead
  of writing. Backs the drift gate `tests/drift/docs/test_changelogs_current.py` — bump
  `properties.yml` without running `docs.update-changelogs` (or `invoke fix`) and this fails.
  A no-op while `CHANGELOG_CATEGORIES` is empty.

### Inline Code Comments
- Comment the *why*, not the *what*
- Reference external docs or issue numbers when a workaround is non-obvious
- Use `# noqa: RULE` or `# pylint: disable=rule-name` with an explanation comment on the same or preceding line

### Instruction Files (`.github/instructions/`)
- One file per concern — see `index.instructions.md`'s "Instruction Files by Domain" list for the
  current, canonical list (not repeated here to avoid a second place going stale)
- Always include a `description` in YAML frontmatter using the "Use when..." pattern
- Use `applyTo` glob only when the instruction is relevant to a specific file type or directory
- Keep instructions actionable and example-driven — prefer short code blocks over prose

## Topic `docs/` User-Content Files
Rules for user-facing files created in `docs/` folders across all topics.

### CSV Files

#### Date Format — MANDATORY

**ALL date fields in CSV files MUST use ISO 8601 format: `YYYY-MM-DD`**

```csv
# ✅ CORRECT
purchase_date
2025-05-15
2026-04-09

# ❌ WRONG — never use these formats
05/15/25
05/15/2025
May 15, 2025
15-05-2025
```

This applies to every date column regardless of what it's named (`purchase_date`, `date`, `start_date`, `end_date`, etc.).

### Unknown / Missing Values

Use `??` for unknown values, never leave a field blank without reason.

```csv
purchase_date,purchase_price
??,??
2025-05-15,"$850 + Tax"
```

### Column Naming

- Use `snake_case` for all column headers
- No spaces in column names

### String Quoting

- Wrap values containing commas, semicolons, or quotes in double quotes
- Use semicolons (`;`) as delimiter within a notes field (not commas)

```csv
notes
"Came with 18-55mm lens; 24.2MP; 1080p video"
```

### Inventory CSV Schema

Standard schema for gear/equipment inventory files:

```
year,make,model,type,color,serial_number,purchase_location,purchase_date,purchase_price,notes
```

- `year` — Model year (integer, e.g. `2025`)
- `make` — Manufacturer (e.g. `Canon`, `Nikon`)
- `model` — Model name/number
- `type` — Category (e.g. `Camera`, `Lens`, `Accessory`)
- `color` — Color if relevant, else leave empty
- `serial_number` — Device serial number
- `purchase_location` — Store or URL (e.g. `bestbuy.com`, `Costco`)
- `purchase_date` — ISO 8601: `YYYY-MM-DD`, or `??` if unknown
- `purchase_price` — Dollar amount with tax note (e.g. `"$850 + Tax"`)
- `notes` — Semicolon-separated details (bundle contents, specs, purpose)
