---
applyTo: "topics/**"
---
# Topics Instructions

## Topic Structure

Topics are organized as a two-level hierarchy under `topics/category/subtopic/`. Each leaf topic contains:

```
topics/<category>/<subtopic>/
├── OPENCODE.md    # AI agent instructions (OpenCode)
├── AGENTS.md      # AI agent instructions (cross-tool: Copilot, Codex, etc.)
├── CLAUDE.md      # AI agent instructions (Claude Code)
├── active.yml     # Active chat tracker (git-ignored)
├── chats/         # AI conversation logs only (YYYYMMDD_title.md format)
└── docs/          # User-facing files of any type (created on request)
```

## Research Document Workflow — CRITICAL

**Default: Research stays in the chat file**
- All research and conversation belongs in the active chat: `chats/YYYYMMDD_title.md`
- **DO NOT automatically create separate research documents**
- Chat logs contain the complete conversation history

**Only create docs/ files when explicitly requested:**
- User says "create a doc with..." → create in `docs/category/filename.md`
- User says "make a domains.csv" → create `docs/domains.csv`
- User says "make a config.json" → create `docs/config.json`
- User does NOT ask for a file → keep everything in the chat file

## File Default Location Rule

**`docs/` = user-facing files of any type. `chats/` = AI conversation logs only.**

Any file the user asks to create goes in `docs/` by default — `.md`, `.csv`, `.txt`, `.json`, `.yml`, or any other type:
- User says "make a domains.csv" → `{active_topic_path}/docs/domains.csv`
- User says "create a headlights.md" → `{active_topic_path}/docs/headlights.md`
- User says "make a config.json" → `{active_topic_path}/docs/config.json`
- Exception: chat files always go in `chats/`; instruction files stay in their defined locations
- Exception: user explicitly specifies a different path → use that path

## File Management

- Work from git-tracked paths only (`topics/`, `agents/`)
- Use ISO 8601 date format: `YYYYMMDD_description.md` for chat files
- Screenshots stored centrally at repo root `screenshots/` — NOT in topic folders
- Never write files outside the repository root (`repo.local` in `properties.yml`) without explicit permission

## Instruction File Sync

When updating topic instructions in a topic directory:
- update `AGENTS.md` for topic-specific guidance
- keep `CLAUDE.md` as a thin pointer to the partner `AGENTS.md` in the same directory
- update `OPENCODE.md` only when OpenCode-specific guidance changes

Topic-specific guidance should live in `AGENTS.md`.

- `CLAUDE.md` should remain a thin pointer to `AGENTS.md`
- `CLAUDE.md` should not need content changes beyond pointing to the partner `AGENTS.md`
- Do not duplicate topic-specific rules in `CLAUDE.md`
- If topic guidance changes, update `AGENTS.md` as the content source of truth and keep `CLAUDE.md` as a pointer

## templates.py Change Rule — CRITICAL

`modules/topic/templates.py` is the single source of truth for all topic instruction file content. It drives what `/topic init` and `/topic update` generate for every topic's OPENCODE.md.

**When you modify anything in `modules/topic/` that affects topic instruction content:**
1. Run fix + test (10/10 required)
2. **Ask the user**: "Should I run `/topic update` to regenerate all topic AGENTS.md files with the new template?"
3. **Check root `AGENTS.md`** — it is hand-maintained and may need manual sync if the change reflects a new policy

This applies any time you touch `templates.py`, `init.py`, `update.py`, or any logic that affects what gets written to topic instruction files.

## Active State Files

- `active.yml` — tracks active chat in a topic (managed by chat scripts, git-ignored)
- `active_topic.yml` — tracks active topic at repo root (git-ignored)
