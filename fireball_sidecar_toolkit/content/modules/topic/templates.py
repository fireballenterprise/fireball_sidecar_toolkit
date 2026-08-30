"""Template generators for topic file content."""

from pathlib import Path

# Repo-relative — never an absolute machine path (see .github/instructions/screenshots.instructions.md)
_SCREENSHOTS_DIR = "screenshots"
_LATEST_SCREENSHOT = f"{_SCREENSHOTS_DIR}/latest.png"

# ---------------------------------------------------------------------------
# Private section helpers - keep each small for linter compliance
# ---------------------------------------------------------------------------


def _hub_instructions_section() -> str:
    """Return a section directing agents to read the .github/instructions/ hub."""
    return """## Project-Wide Instructions — Always Read First

`AGENTS.md` at the repo root carries the project overview, the full instruction-file map, and the
golden rules. Read the scoped file that fits the task before working:

- **Topics & research workflow**: `.github/instructions/topics.instructions.md`
- **Markdown style**: `.github/instructions/markdown.instructions.md`
- **CSV file standards**: `.github/instructions/csv.instructions.md`

Other files in `.github/instructions/` cover Python, modules, tasks, tests, prompts, git, review,
screenshots, versioning, and the personal/travel profile — see the map in root `AGENTS.md`."""


def _read_first_section(ancestors: list[tuple[str, str]]) -> str:
    """Return a 'Read First' block listing ancestor AGENTS.md files.

    Args:
        ancestors: List of (label, path) tuples from root down to immediate parent.
                   e.g. [("Workshop", "topics/workshop/AGENTS.md")]

    Returns:
        Formatted Read First markdown section.
    """
    lines = [
        "## Read First",
        "",
        "Before working in this topic, read the following AGENTS.md files for context:",
        "",
    ]
    for label, path in ancestors:
        lines.append(f"- **{label}**: `{path}`")
    lines.append("")
    return "\n".join(lines)


def _screenshot_section() -> str:
    """Return the Screenshots Workflow section."""
    return f"""## Screenshots Workflow

When user types `ss` or `/ss` to view a screenshot, follow these steps IN ORDER:

### Step 1 - Run the screenshot command
Use `/ss` (alias for `/screenshots view`). It copies the most recent screenshot to `latest.png`.

### Step 2 - Read the copied file (path is relative to the repo root)
```
{_LATEST_SCREENSHOT}
```
Only read this AFTER step 1 completes successfully.

### Step 3 - Describe what you see
Describe the image content to help with the user's research.

**Common mistake to avoid:**
```
\u274c WRONG: Read latest.png directly without running /ss first
\u2705 RIGHT: Run /ss \u2192 THEN read latest.png
```"""


def _slash_command_section() -> str:
    """Return the Modifying Slash Commands section."""
    return """## Modifying Slash Commands - CRITICAL WORKFLOW

**IMPORTANT:** AI tools cache command files. After editing a command file in `.github/prompts/`
(or a mirror like `.claude/commands/`), restart your AI tool before testing \u2014 changes are not
hot-reloaded. `.github/prompts/` is the source of truth; see `ai_commands.instructions.md`.

```
\u274c WRONG: Edit file \u2192 Test immediately \u2192 Doesn't work \u2192 Get confused
\u2705 RIGHT: Edit file \u2192 Restart AI tool \u2192 Test \u2192 Works
```"""


def _workflow_section() -> str:
    """Return the AI Tool Workflow section."""
    return f"""## Chat Workflow

When working in this topic:

1. **Starting a chat**: Use `/chat start` to initialize a new research session
   - **AUTO-CLOSE**: Automatically closes any active chat before starting
   - Previous chat is committed with message "Research session: [title]"
2. **Screenshots**: Type "ss" or "/ss" to examine the latest screenshot
   - **STEP 1 - MANDATORY**: Run `/ss` (copies newest file to latest.png)
   - **STEP 2**: Read `{_LATEST_SCREENSHOT}` at the repo root (only AFTER step 1 - otherwise you get a stale image)
   - **NEVER** read latest.png without running /ss first
3. **Resuming work**: Use `/chat resume` to continue a previous chat
   - **AUTO-CLOSE**: Automatically closes any active chat before resuming
   - Previous chat is committed with message "Research session: [title]"
   - You can pass a pattern (example: `/chat resume home_security_camera_solution`)
4. **Saving work**: Use `/chat end` to save complete chat log and deactivate session
   - **CRITICAL**: AI agent MUST format and append complete chat log to file before calling `/chat end`
   - See `/chat end` workflow below for detailed instructions
   - `/chat end` saves to file but does NOT commit or push - use git commands when ready
5. **Closing session**: Use `/chat end` to save chat log and clear active status
   - Then start new session with `/chat start` to clear context and reset tokens
   - Or commit changes manually when ready (git add/commit/push)

**Note**: `/chat start` and `/chat resume` now automatically close active chats - no need to manually run `/chat end` first."""


def _commands_section() -> str:
    """Return the Available Commands section."""
    return """## Available Commands

Slash commands (routed to Python modules):
- `/chat start` - Start a new chat session (auto-closes active chat)
- `/chat end` - Save complete chat log to file and deactivate session (does not commit/push)
- `/chat resume` - Resume a previous chat (auto-closes active chat)
- `/chat list` - List all chats in this topic
- `/repo pull` - Pull updates from git remote and iCloud
- `/repo push` - Push changes to git remote and iCloud
- `/screenshots view` - Copy latest screenshot to latest.png (alias: `/ss`)
- `/financials update_card_limit` - Update credit card limit (alias: `/update_card_limit`)"""


def _chat_end_section() -> str:
    """Return the /chat end Workflow section."""
    return """## `/chat end` Workflow - CRITICAL AI AGENT INSTRUCTIONS

When `/chat end` is called, the AI agent MUST follow this exact sequence:

### Step 1: Format the Complete Chat Log

Create a markdown formatted log of the ENTIRE chat from start to finish:

```markdown
## Chat Log

---
**[YYYY-MM-DD HH:MM:SS] User:**
[User's message]

---
**[YYYY-MM-DD HH:MM:SS] Assistant:**
[Assistant's complete response including code blocks, explanations, etc.]

[Continue for ALL messages...]
```

### Step 2: Append to Chat File

- Read the current chat file (from chats/ directory, filename stored in active.yml)
- Use Edit or Write tool to append the formatted chat log
- Preserve ALL formatting: code blocks (```language), bold, lists, etc.
- Include timestamps for every message
- Maintain chronological order

### Step 3: Confirm and Stop

- After updating the file, confirm it is done in a single short response
- **DO NOT** tell the user to "run `/chat end` again" — the user already ran it; fixing the file is sufficient
- The `/chat end` command will automatically re-validate on the next invocation; that is the user's action, not yours
- **NOTE**: Does NOT commit or push changes - use git commands explicitly when ready
- **TIP**: After ending, start a new chat with `/chat start` to clear context and reset tokens

### Chat Log Format Requirements

- Horizontal rules (`---`) between messages for visual separation
- Bold timestamps and speaker labels: `**[timestamp] Speaker:**`
- Preserve code blocks with syntax highlighting
- Include tool outputs and system messages
- Complete context for future reference

### What /chat end Does

1. ✅ Validates that the complete chat log was saved to the chat file
2. ✅ Clears the active.yml file to deactivate the current session
3. ❌ Does NOT commit changes to git (commit manually when ready)
4. ❌ Does NOT push to remote (push manually when ready)"""


def _file_org_section() -> str:
    """Return the File Organization section."""
    return f"""## File Organization

- **chats/**: Saved AI chat logs with complete chat history (YYYYMMDD_title.md format)
- **docs/**: User-requested summary documents and reference materials
- **AGENTS.md**: Topic instruction source of truth
- **CLAUDE.md**: Thin pointer to the partner AGENTS.md in the same directory

**Path rule**: Treat the active topic folder as the default working root for all user-requested file paths.
- If user asks for `docs/foo.md`, create `topics/<active_topic>/docs/foo.md`
- If user asks for `scripts/blah.sh`, create `topics/<active_topic>/scripts/blah.sh`
- Only write to repo-root paths when the user explicitly says root/repo-level.

**File default location rule**: ANY file the user asks to create goes in `docs/` by default — `.md`, `.csv`, `.txt`, `.json`, `.yml`, or any other type.
- User says "make a domains.csv" → create `topics/<active_topic>/docs/domains.csv`
- User says "create a headlights.md" → create `topics/<active_topic>/docs/headlights.md`
- User says "make a config.json" → create `topics/<active_topic>/docs/config.json`
- **Core distinction**: `docs/` = user-facing files of any type; `chats/` = AI conversation logs only
- Exception: chat files always go in `chats/`, instruction files stay in their defined locations
- Exception: user explicitly specifies a different path → use that path

**Note**: Screenshots are stored centrally at repo root (`{_SCREENSHOTS_DIR}/`), NOT in topic-specific folders.

### Date Format — MANDATORY

- **Filenames**: Use `YYYYMMDD_description.md` (e.g. `20260409_filming_gear.md`)
- **CSV date fields**: Use ISO 8601 `YYYY-MM-DD` (e.g. `2025-05-15`) — see `.github/instructions/csv.instructions.md`
- **NEVER** use MM/DD/YY or MM/DD/YYYY formats in any file

### Research Document Workflow - CRITICAL

**Default: Research stays in the chat file**
- All research and conversation belongs in the active chat: `chats/YYYYMMDD_title.md`
- Chat logs contain the COMPLETE conversation history for AI context later
- **DO NOT automatically create separate research documents**

**Only create docs/ files when user explicitly requests them:**
- User: "create a doc with the summary" → Create in current topic `docs/category/filename.md`
- User: "give me a markdown file..." → Create the requested file in current topic `docs/`
- User: "make a domains.csv" → Create in current topic `docs/domains.csv`
- User: "make a config.json" → Create in current topic `docs/config.json`
- User does NOT ask for a file → Keep everything in chat

**ALL files go in `docs/` — any type: `.md`, `.csv`, `.txt`, `.json`, `.yml`, etc.**

**Purpose of each folder:**
- **chats/**: AI conversation logs only — for AI to read and understand context
- **docs/**: User-facing files of any type — summaries, data, configs, references (when requested)

**Example:**
- ❌ WRONG: Auto-creating `docs/research.md` during conversation
- ❌ WRONG: Creating any file directly in the topic root
- ✅ RIGHT: Keep all research in `chats/20260226_cameras.md` unless user asks for a file
- ✅ RIGHT: When requested, create `docs/domains.csv`, `docs/config.json`, or `docs/home_security/pricing.md`"""


# ---------------------------------------------------------------------------
# Private builder - assembles all sections
# ---------------------------------------------------------------------------


def _build_agents_md(
    topic_name: str,
    topic_category: str,
    topic_purpose: str,
    topic_type: str,
    ancestors: list[tuple[str, str]] | None = None,
) -> str:
    """
    Build full topic AGENTS.md content from section helpers.

    Args:
        topic_name: Display name of the topic.
        topic_category: Category the topic belongs to.
        topic_purpose: Purpose/description of the topic.
        topic_type: Type classification (e.g. Research and Documentation).
        ancestors: Optional list of (label, path) tuples for parent AGENTS.md files.
                   When provided, a 'Read First' block is prepended.

    Returns:
        Complete AGENTS.md content string.
    """
    parts = [
        f"# AI Agent Instructions for {topic_name}",
        "",
        "**Sync Rule**: `AGENTS.md` is the topic content source of truth; `CLAUDE.md` is a thin pointer to it.",
        "",
    ]

    # Always inject hub instructions so agents read project-wide rules
    parts.append(_hub_instructions_section())

    # Inject Read First block if ancestor AGENTS.md files exist
    if ancestors:
        parts.append(_read_first_section(ancestors))

    parts += [
        "## Topic Information",
        "",
        f"**Name**: {topic_name}",
        f"**Category**: {topic_category}",
        f"**Type**: {topic_type}",
        f"**Purpose**: {topic_purpose}",
        "",
        "## Working Environment",
        "",
        "- Research and troubleshooting workspace; chat logs and `docs/` files are the artifacts",
        "- Git for version control and optional iCloud sync via `/push`",
        "- Works with any AI tool that reads `AGENTS.md` / `CLAUDE.md`",
        "",
        _workflow_section(),
        "",
        _commands_section(),
        "",
        _slash_command_section(),
        "",
        _chat_end_section(),
        "",
        _file_org_section(),
        "",
        _screenshot_section(),
        "",
    ]

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def agents_md(
    topic_path: str,
    description: str | None = None,
    repo_root: Path | None = None,
) -> str:
    """
    Generate AGENTS.md content (tool-neutral) for a leaf topic.

    Suitable for Claude Code, GitHub Copilot, Codex, Cursor, and other AI tools that read AGENTS.md.

    Args:
        topic_path: Relative path to topic from topics/ root.
        description: Optional custom description for the topic.
        repo_root: Optional absolute path to the repo root (enables ancestor AGENTS.md detection).

    Returns:
        Formatted AGENTS.md content string.
    """
    path = Path(topic_path)
    topic_name = path.name.replace("_", " ").title()
    topic_category = str(path.parent).replace("_", " ").title() if path.parent != Path(".") else "General"

    if description:
        topic_purpose = description
        topic_name = description
    else:
        topic_purpose = f"working with {topic_name}"

    ancestors: list[tuple[str, str]] = []
    if repo_root is not None:
        topics_root = repo_root / "topics"
        ancestor_path = Path()
        for part in path.parts[:-1]:
            ancestor_path = ancestor_path / part
            candidate = topics_root / ancestor_path / "AGENTS.md"
            if candidate.exists():
                label = part.replace("_", " ").title()
                rel_path = f"topics/{ancestor_path}/AGENTS.md"
                ancestors.append((label, rel_path))

    return _build_agents_md(
        topic_name,
        topic_category,
        topic_purpose,
        "Research and Documentation",
        ancestors or None,
    )


def claude_md(
    topic_path: str,  # pylint: disable=unused-argument
    description: str | None = None,  # pylint: disable=unused-argument
    repo_root: Path | None = None,  # pylint: disable=unused-argument
) -> str:
    """
    Generate CLAUDE.md pointer content for a leaf topic.

    CLAUDE.md is a thin pointer that directs Claude Code to read AGENTS.md.
    AGENTS.md is the single source of truth — no content is duplicated here.

    Args:
        topic_path: Unused. Kept for API consistency with agents_md().
        description: Unused. Kept for API consistency with agents_md().
        repo_root: Unused. Kept for API consistency with agents_md().

    Returns:
        CLAUDE.md pointer content string.
    """
    return (
        "# Claude Code Instructions\n\n"
        "See [AGENTS.md](AGENTS.md) in this directory for full instructions.\n\n"
        "`AGENTS.md` is the single source of truth. Always read and update `AGENTS.md` "
        "— do not duplicate content here.\n"
    )
