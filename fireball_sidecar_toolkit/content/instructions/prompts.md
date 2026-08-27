---
applyTo: ".opencode/command/**,.claude/commands/**,.clinerules/workflows/**,.github/prompts/**"
---
# AI Prompts Instructions

Standards for the AI custom prompts / slash commands synced across all four tool directories
(`.github/prompts/`, `.claude/commands/`, `.opencode/command/`, `.clinerules/workflows/`).

## Architecture

Commands are the AI-facing entrypoint layer described in `.github/instructions/logic.instructions.md`
(Core Principle + The Stack) — thin wrappers only, no business logic. See that file for
why prompts are the AI's decision-capture layer, and how this differs from
`tasks.instructions.md`'s plain CLI automation.

## Required Frontmatter

### OpenCode (.opencode/command/*.md)
```yaml
---
description: Brief description
agent: general
subtask: false  # CRITICAL — prevents Task tool recursion
slash_command: /command_name
---
```

### Claude Code (.claude/commands/*.md)
```yaml
---
description: Brief description
---
```
Claude Code uses the filename as the command name. Extra frontmatter fields are ignored.

### GitHub Copilot (.github/prompts/*.prompt.md)
```yaml
---
name: command_name
description: Brief description
argument-hint: arg1 | arg2 [optional]
agent: agent
---
```

### Cline (.clinerules/workflows/*.md)
No frontmatter — Cline workflows are plain markdown body only. The filename (minus extension) is
the command name.

## Command Body

OpenCode, Claude Code, and Copilot use the same inline-execution syntax:

```
!`uv run --no-sync python -m modules.your_module.route "$ARGUMENTS"`
```

The `!` prefix runs bash. `$ARGUMENTS` receives everything after the command name.

Cline doesn't support inline `!`...`` execution — its workflow body instead tells the agent to run
the command explicitly:

```markdown
Run this terminal command:

\`\`\`
uv run --no-sync python -m modules.your_module.route "$ARGUMENTS"
\`\`\`
```

## Creating a New Command

1. Create Python module: `modules/your_module/your_task.py` (ALL logic here)
2. Create router: `modules/your_module/route.py` (argument dispatch)
3. Create command files in all four tool dirs with the thin wrapper body
4. Run `uv run invoke fix && uv run invoke test` (must be 10/10 for .py changes)

## Cache Restart Requirement

AI tools cache command files at startup. After editing a command file, restart the AI tool before testing.

## uv --no-sync Flag

All `uv run` calls in commands MUST use `--no-sync`:
```
✅ uv run --no-sync python -m modules.chat.route "$ARGUMENTS"
❌ uv run python -m modules.chat.route "$ARGUMENTS"
```

## How Slash Commands Route

```
User: /chat resume wire_tunnels
  ↓
AI tool reads command file (.opencode/command/chat.md, .claude/commands/chat.md,
  .clinerules/workflows/chat.md, or .github/prompts/chat.prompt.md)
  ↓
Command file executes: uv run --no-sync python -m modules.chat.route "resume wire_tunnels"
  ↓
Router (modules/chat/route.py) dispatches: modules.chat.resume --pattern="wire_tunnels"
  ↓
Python function receives: pattern="wire_tunnels"
```

## Creating a New Command — Full Workflow

### Step 1: Create Python Module (ALL logic here)

```python
# modules/your_module/your_task.py
"""Your task description."""

from modules.common import cli


@cli.command()
@cli.option("--argument", required=False, help="Description")
def main(argument: str | None = None) -> None:
    """Your task logic here."""
    cli.echo(f"Processing: {argument}")
```

### Step 2: Create Router Module

```python
# modules/your_module/route.py
import shlex
import subprocess
import sys

from modules.common.route_utils import build_env, find_repo_root


def main() -> int:
    raw_args = sys.argv[1] if len(sys.argv) > 1 else ""
    args = shlex.split(raw_args)
    repo_root = find_repo_root()
    env = build_env(repo_root)
    cmd = [sys.executable, "-m", "modules.your_module.your_task", *args]
    return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
```

### Step 3: Create Command Files in All Four Tool Dirs

Create equivalent files in `.opencode/command/`, `.claude/commands/`, `.clinerules/workflows/`, and
`.github/prompts/` using the appropriate frontmatter format (see above), with the same execution
body (adjusted for Cline's non-`!` syntax, see Command Body above):

```
!`uv run --no-sync python -m modules.your_module.route "$ARGUMENTS"`
```

### Step 4: Test and Commit

```bash
uv run --no-sync invoke fix && uv run --no-sync invoke test  # must be 10/10
```

**DO NOT:**
- ❌ Put business logic in slash command markdown files
- ❌ Write bash scripts directly in slash commands
- ❌ Use `subtask: true` (causes Task tool recursion)

## Modifying Commands — Cache Restart Required

AI tools cache command files at startup. After editing a command file you MUST restart the AI tool.

```
❌ WRONG: Edit file → Test immediately → Doesn't work → Get confused
✅ RIGHT: Edit file → Restart AI tool → Test → Works
```

## Command → Router → Module Mapping

### Chat
```
/chat start [title]    → modules.chat.route → modules.chat.start
/chat list [sort]      → modules.chat.route → modules.chat.list
/chat resume [pattern] → modules.chat.route → modules.chat.resume
/chat end              → modules.chat.route → modules.chat.end
```

### Repo
```
/repo push             → modules.repo.route → modules.repo.push
/repo pull             → modules.repo.route → modules.repo.pull
/repo cleanup          → modules.repo.route → modules.repo.cleanup
/repo set_screenshots  → modules.repo.route → modules.repo.set_screenshots
/repo view_screenshot  → modules.repo.route → modules.repo.view_screenshot
/rebase                → invoke repo.rebase → modules.repo.rebase
/squash                → invoke repo.squash → modules.repo.squash
/push (alias)          → /repo push
/pull (alias)          → /repo pull
/ss (alias)            → /repo view_screenshot
```

### Topic
```
/topic list              → modules.topic.route → modules.topic.list
/topic switch <path>     → modules.topic.route → modules.topic.switch
/topic <path>            → modules.topic.route → modules.topic.switch
/topic init               → modules.topic.route → modules.topic.init
/topic update             → modules.topic.route → modules.topic.update
```

### Financials
```
/financials              → modules.financials.route → modules.financials (no args)
/update_card_limit       → (AI-guided) → modules.financials.update_card_limit
```

### Resume
```
/resume create [--slug value]  → modules.employment.route → modules.employment.resume --action=create
/resume update [--slug value]  → modules.employment.route → modules.employment.resume --action=update
/resume sync [--file path]     → modules.employment.route → modules.employment.resume --action=sync
/resume setup                  → modules.employment.route → modules.employment.resume --action=setup
/resume clean                  → modules.employment.route → modules.employment.resume --action=clean
```
`create`/`update` copy a template/latest-draft JSON file into `docs/resume/raw/` and print it — the
AI agent edits that file's content per `resume.prompt.md`'s instructions. `sync` is fully
deterministic: it PATCHes the edited JSON into the local Reactive Resume Docker service via its
REST API and downloads the rendered PDF into `docs/resume/`, archiving any previous PDF.
`setup`/`clean` manage that Docker service (idempotent bring-up / stop-without-data-loss).
`create`/`update`/`sync` auto-start the service if needed. See
`topics/employment/docs/resume/resume_guidelines.md` and `modules/employment/README.md`.

### Version Checks & Upgrades
```
/update [libs|python|workflows]  → invoke ver.update → modules.versioning.{libs,python,workflows}
/upgrade [python|libs|sync]      → invoke upgrade    → modules.versioning.upgrade
```
`/update` and `invoke ver.update`/`invoke update` are equivalent, as are `/upgrade` and
`invoke ver.upgrade`/`invoke upgrade` — mirrors `apt update && apt upgrade`.

### Template Sync
```
/template [pull]  → modules.template.route → modules.template.pull
/template push    → modules.template.route → modules.template.push
```
