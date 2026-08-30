# Chat Manager
The chat module handles the complete lifecycle of research chat sessions within the AI research workspace.

## Features
- **Start Chats**: Initialize new research sessions with timestamped files
- **End Chats**: Save full chat logs and commit to git
- **List Chats**: Browse existing chats with summaries
- **Resume Chats**: Continue previous research sessions
- **Active Tracking**: Tracks currently active chat to prevent accidental switching
- **Auto-Detection**: Automatically detects topic context from current directory
- **Screenshot Integration**: Uses centralized screenshots folder at repo root
- **Full Chat Logs**: AI agents save complete conversation history with timestamps

## Commands
### `/chat start`
Initialize a new research chat session in a topic directory.

**Usage:**
```
/chat start [title]
```

**Arguments:**
- `title` (optional) - Chat title. If not provided, you'll be prompted to enter one.

**Workflow:**
1. Validates current location is within a `topics/` subdirectory
2. **Automatically ends any active chat** - saves and commits existing work locally
3. Uses provided title or prompts user for chat title if not given
4. Generates filename with ISO 8601 date: `YYYYMMDD_title.md`
5. Creates `chats/` and `docs/` directories if needed
6. Creates chat markdown file with template
7. Creates `active.yml` tracker file with chat metadata
8. Configures macOS screenshot location to central repo screenshots/ folder
9. Stores chat filename for use by `/end`

**Examples:**
- `/start import_print_profiles` - Creates `20251211_import_print_profiles.md`
- `/start automating_my_ai_agents` - Creates `20251211_automating_my_ai_agents.md`
- `/start` - Prompts for title
- User input: "automating my ai agents" → `20251211_automating_my_ai_agents.md`
- Location: `chats/20251211_automating_my_ai_agents.md`

**Template Structure:**
```markdown
# [Title]

Date: [Full date]
Topic: [topic/path]

## Overview

[This section will be filled in during the chat]

## Chat Log

[AI agent will append full conversation here when /end is called]
```

**Requirements:**
- Must be run from within a `topics/` subdirectory
- Valid topic path pattern: `*/topics/[category]/[topic_name]`

**Module:** Uses `modules.toolkit.chat.start` for chat initialization (via `/chat start`)

### `/chat end`
Save full chat log to file and commit changes locally.

**CRITICAL WORKFLOW - AI Agent Instructions:**

When `/chat end` is called, the AI agent MUST follow this exact sequence:

1. **Format the complete chat log** in this markdown structure:
   ```markdown
   ## Chat Log
   
   ---
   **[YYYY-MM-DD HH:MM:SS] User:**
   [User's message]
   
   ---
   **[YYYY-MM-DD HH:MM:SS] Assistant:**
   [Assistant's complete response including all code blocks, tool outputs, etc.]
   
   [Continue for entire conversation...]
   ```

2. **Append the chat log** to the active chat file:
   - Read the current chat file (created by `/start`)
   - Use Edit or Write tool to append the formatted chat log
   - Preserve timestamps, code blocks, and formatting
   - Include ALL messages from start to `/end` command

3. **Call the end command** to commit changes:
    - Run: `/chat end`
   - This executes git operations:
     - `git status` to review changes
     - `git add -A` to stage all changes
     - `git commit -m "Research session: [title]"`
     - (No push) Run `/push` separately when ready to sync
     - Removes `active.yml` tracker file

**Validation gate in `/chat end`:**
- Refuses to finish if chat file context is incomplete
- Requires:
  - `## Overview` updated (not placeholder text)
  - `## Chat Log` section present
  - timestamped log entries (`**[YYYY-MM-DD HH:MM:SS] User/Assistant:**`)

**Chat Log Format Details:**
- Use `---` horizontal rules between messages
- Bold timestamps and speaker labels: `**[timestamp] Speaker:**`
- Preserve code blocks with syntax highlighting (```bash, ```python, etc.)
- Include tool outputs and system messages
- Maintain chronological order
- Capture complete context for future reference

**Auto-Detection:**
- Uses chat file from active.yml (created by `/start`)
- Validates file exists before appending

**Error Handling:**
- Handles commit edge cases gracefully
- Confirms local save and clear of active state
- Warns if no active chat found

**Module:** Uses `modules.toolkit.chat.end` for git operations

### `/chat list`
List chat files in the current topic's chats folder with summaries.

**Workflow:**
1. Auto-detects topic directory from current location
2. Checks for `active.yml` - displays active chat at top with ⭐ indicator
3. Lists all chat files in `chats/` folder
4. Shows first 2 lines of each file as summary
5. Sorts by newest first (default)

**Sort Options:**
- `newest_first` - Most recent chats first (default)
- `oldest_first` - Oldest chats first
- `alphabetical` - Alphabetically by filename

**Display Format:**
```
⭐ ACTIVE CHAT
20251211_automating_my_ai_agents.md
  Started: 2025-12-11 16:30:45
  Status: active

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

20251210_legal_research.md
  Summary: Research session on past legal records...
  Documented 3 felony convictions and sealed records...
```

### `/chat resume`
Resume an existing chat from the chats folder.

**Usage:**
```
/resume [filename|pattern]
```

**Arguments:**
- `filename|pattern` (optional) - Filename or date pattern to match. If not provided, lists all chats to choose from.

**Workflow:**
1. Auto-detects topic directory from current location
2. Checks for existing active chat - warns if one exists
3. If filename provided, loads that chat directly
4. If pattern provided (e.g., "import_print"), searches for matching chats
5. If no argument, lists available chats with summaries
6. Prompts user to select which chat to resume if multiple matches
7. Updates `active.yml` tracker with resumed chat metadata
8. Loads selected chat into current session context
9. User can continue adding to the chat
10. Use `/end` when finished to append new chat log and save updates

**Resilience behavior:**
- If `active.yml` exists but is malformed/stale (e.g., `filename: null`), `/chat resume` ignores it and proceeds
- `/chat list` only shows an active chat when `active.yml` has valid `filename`, `title`, and `topic` values

**Features:**
- Shows summaries with each chat option
- Sorts by newest first (default)
- Seamlessly continues previous research sessions
- Supports partial filename matching

**Examples:**
- `/resume 20251211_import_print_profiles` - Resume specific chat
- `/resume import_print` - Resume chat matching "import_print"
- `/resume` - Lists all chats to choose from

**Use Cases:**
- Continue multi-day research projects
- Add new findings to existing documentation
- Review and expand on previous work

## Directory Structure
Chats are organized within topic directories:
```
topics/
├── mac/
│   └── fusion/
│       ├── chats/
│       │   ├── 20251211_modeling_techniques.md
│       │   └── 20251210_setup_guide.md
│       ├── docs/
│       └── active.yml (when chat is active)
├── business/
│   └── accounting/
│       ├── chats/
│       │   └── 20251208_quickbooks_setup.md
│       ├── docs/
│       └── active.yml (when chat is active)
└── legal/
    └── past_record/
        ├── chats/
        │   └── 20251211_legal_research.md
        ├── docs/
        └── active.yml (when chat is active)

screenshots/  # Centralized at repo root (shared by ALL topics)
├── latest.png
└── Screenshot 2026-01-04 at 3.00.09 PM.png
```

## Active Chat Tracking
The chat manager tracks the currently active chat using an `active.yml` file in each topic directory.

**active.yml Format:**
```yaml
filename: 20251211_tracking_feature.md
title: Implement Active Chat Tracking
started: 2025-12-11 16:30:45
topic: help/word_smith
status: active
```

**Behavior:**
- Created by `/chat start` when initializing new chat
- Updated by `/chat resume` when loading existing chat
- Displayed by `/chat list` at top with ⭐ indicator
- Removed by `/chat end` when saving work
- **Automatically handled by `/chat start`** - previous chat is ended and new one becomes active
- Invalid or incomplete tracker data is treated as no active chat

**Benefits:**
- Clear visibility of active work session
- Prevents data loss from switching chats
- Maintains session context across commands
- Local state only (not tracked in git)

## Screenshot Workflow
When `/start` or `/set_screenshots` runs:
1. Configures macOS: `defaults write com.apple.screencapture location ${repo_local}/screenshots`
2. Restarts System UI: `killall SystemUIServer`
3. All future screenshots auto-save to centralized repo `screenshots/` folder (shared by ALL topics)

During chat:
- User takes screenshot with macOS: `Cmd+Shift+4` saves to central `screenshots/`
- User types "ss" to have AI view the latest screenshot
- AI reads from centralized `screenshots/latest.png`
- Screenshots are referenced in chat context

## File Naming Convention
- **Format**: `YYYYMMDD_slug.md`
- **Date**: ISO 8601 format (e.g., 20251211)
- **Slug**: Lowercase, underscores, no special characters
- **Extension**: Always `.md` (Markdown)

**Examples:**
- "Automating AI Agents" → `20251211_automating_ai_agents.md`
- "Legal Research" → `20251211_legal_research.md`
- "QuickBooks Setup" → `20251211_quickbooks_setup.md`

## Git Integration
Chat commands use git for local version control:

**Commit Format:**
```
Research session: [brief description]
```

**Example Commits:**
```
Research session: automating my ai agents
Research session: legal research on past records
Research session: fusion modeling techniques
```

**Benefits:**
- Automatic version control
- Sync across devices via remote repository
- Integration with iCloud Obsidian folder
- Full history of research sessions
- Complete chat logs preserved with timestamps

## Dependencies
- `topic` - For topic navigation and initialization

## Configuration
Default settings in `config.yml`:
- `topics_dir`: "topics/"
- `chats_subdir`: "chats"
- `screenshots_subdir`: "screenshots"
- `date_format`: "YYYYMMDD"

## Permissions Required
- `file_read` - Read chat files
- `file_write` - Create/update chat files
- `directory_create` - Create chats/screenshots folders
- `directory_list` - List chat files
- `git_commit` - Commit changes
- `git_push` - Push to remote (used by `/push`, not `/chat end`)
- `bash_execute` - Configure screenshot location

## Best Practices
1. **Start Every Session**: Use `/chat start` at the beginning of research
2. **Descriptive Titles**: Choose clear, searchable chat titles
3. **Seamless Switching**: Use `/chat start <new_title>` to automatically end current chat and start new one
4. **Screenshot Context**: Type "ss" when referencing visual elements
5. **Resume When Needed**: Use `/chat resume` for specific previous chats
6. **Complete Logs**: AI agents automatically save full chat history with timestamps
7. **Final Save**: Use `/chat end` only when completely done with research session

## Related Commands
- `/topic` - Switch between topics or create new ones
- `/pull` - Pull updates from git remote and iCloud
- `/push` - Push changes to git remote and iCloud

## Notes
- Commands are thin wrappers routed to Python modules; work with any AI tool
- Designed for research and documentation workflows
- Multi-AI collaboration friendly (Claude, Copilot, etc.)

## Files
- `start.py` - Initialize new chat with auto-ending (used by `/chat start`)
- `list.py` - List chats with summaries (used by `/chat list`)
- `resume.py` - Resume existing chat (used by `/chat resume`)
- `end.py` - End chat, save log, and commit to git (used by `/chat end`)
- `README.md` - This file
