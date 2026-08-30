# Topic Manager Agent
The topic module handles navigation and management of topic directories within the AI agents workspace.

## Features
- **Topic Discovery**: List all available topics in organized tree format
- **Smart Navigation**: Navigate to existing topics or create new ones
- **Auto-YAML Update**: Automatically updates topics_list.yml when new topics are created
- **Auto-Initialization**: Automatically initializes structure for new topics
- **Auto-Chat Management**: Automatically saves/resumes chats when switching topics
- **Path Validation**: Ensures proper topic directory structure

## Commands
### `/topic list`
Display all available topics from the repository in a tree format.

**Usage:**
```
/topic list
```

**Workflow:**
1. Reads `topics/topics_list.yml`
2. Parses YAML structure
3. Displays topics organized by category with color-coded tree view
4. Shows currently active topic with ⭐ indicator

**Output Example:**
```
📚 Available Topics
==================

⭐ Active Topic: mac/fusion

financials/
  budget/
  income_tax/
  investments/

mac/
  ├─ ⭐ fusion
  ├─ blender
  └─ obsidian
```

**Use Cases:**
- Discover available topics before switching
- See organizational structure of the repository
- Find the correct path for `/topic switch` command

### `/topic switch <path>` or `/topic <path>`
Switch to specific topic with automatic chat management.

**Usage:**
```
/topic switch mac/fusion
/topic mac/fusion          # shorthand
```

**Workflow:**
1. **Auto-saves current chat** (if active) - commits and pushes changes
2. **Validates topic exists** or offers fuzzy matches for typos
3. **Creates new topic** if doesn't exist (with user confirmation)
4. **Updates active_topic.yml** tracker at repo root
5. **Loads new topic context** - reads AGENTS.md files
6. **Auto-resumes active chat** in new topic (if exists)

**Examples:**
- `/topic switch mac/fusion` → Switch to Fusion 360 topic
- `/topic financials/budget` → Switch to budget topic
- `/topic travel/2026_japan` → Switch to Japan travel planning

**Features:**
- **Intelligent fuzzy matching** - helps with typos
- **Each topic remembers its own active chat**
- **Safe switching** - all work is automatically saved
- **Context loading** - AI gets topic-specific instructions

### `/topic init [description]`
Initialize topic structure in current directory with AI instruction files and folders.

**Usage:**
```
/topic init
/topic init "Fusion 360 modeling and design"
```

**Workflow:**
1. Validates current directory is under `topics/`
2. Creates required directories:
   - `chats/` - For conversation history files
   - `docs/` - For documentation and reference files
3. Creates AI instruction files:
   - `AGENTS.md` - topic-specific AI instructions
4. Prompts to overwrite if files already exist
5. Updates `topics_list.yml` with new topic entry

**Examples:**
- Initialize a new topic after manual directory creation
- Re-initialize an existing topic with fresh instruction files
- Set up AI instructions for a topic created outside of `/topic switch`

### `/topic update [--dry-run] [--current-only]`
Update AGENTS.md files across all topics with latest templates.

**Usage:**
```
/topic update                    # Update all topic AGENTS.md files
/topic update --dry-run          # Preview changes without applying
/topic update --current-only     # Update only current topic
```

**Workflow:**
1. Scans all topics for AGENTS.md files
2. Updates files with latest template structure
3. Preserves topic-specific customizations
4. Shows summary of files updated

**Use Cases:**
- Roll out documentation updates across all topics
- Ensure consistent AGENTS.md structure
- Preview template changes before applying
- Fast workflow (no git operations)

## Directory Structure
Topics are organized under `topics/` with hierarchical structure:
```
topics/
├── mac/
│   ├── fusion/
│   └── affinity_designer_2/
├── financials/
│   ├── budget/
│   └── income_tax/
└── travel/
    └── 2026_japan/
```

## Dependencies
- `start_conversation` - Conversation management

## Files
- `list.py` - Display all topics from YAML in tree format (used by `/topic list`)
- `switch.py` - Switch between topics with fuzzy matching (used by `/topic switch`)
- `init.py` - Initialize topic with AI instruction files (used by `/topic init`)
- `update.py` - Update topic AGENTS.md files with latest templates (used by `/topic update`)
- `update_list.py` - Update topics_list.yml when new topics are created (used by `/topic update_list`)
- `templates.py` - Template functions for creating AI instruction files
- `README.md` - This file

---

## templates.py Change Rule — CRITICAL
`templates.py` is the single source of truth for all topic instruction file content. It drives what `/topic init` and `/topic update` generate for every topic's AGENTS.md.

**When you modify anything in `modules/toolkit/topic/` that affects topic instruction content:**
1. Run fix + test (10/10 required)
2. **Ask the user**: "Should I run `/topic update` to regenerate all topic AGENTS.md files with the new template?"
3. **Check root `AGENTS.md`** — it is hand-maintained and may need manual sync if the change reflects a new policy

This applies any time you touch `templates.py`, `init.py`, `update.py`, or any logic that affects what gets written to topic instruction files.

## Active State Files
These files are managed by this module and are git-ignored:

- `active.yml` — per-topic tracker for the currently active chat (lives inside each topic directory)
- `active_topic.yml` — repo-root tracker for the currently active topic
