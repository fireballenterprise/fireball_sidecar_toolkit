---
name: topic
description: Use for switching the active planning-topic workspace, or listing/creating/initializing/updating topics under topics/. Equivalent to /topic.
---

# Topic Workspace Workflow
Use this file as source of truth: `.ai/shared/commands/topic.md`

When the user asks to switch topics, list topics, create a new topic, or run a `/topic`
equivalent, read that file and follow it.

- Switch: `switch <path>` (or bare `<path>`)
- List: `list` (active only) / `list all` (every topic)
- Create: `new <path> [description] [--instructions=a,b]`
- Initialize in place: `init [description] [--instructions=a,b]`
- Regenerate AGENTS.md/CLAUDE.md from template + `topic_meta`: `update [--dry-run] [--current-only] [--topic=a,b]`

Run the router from the repo root:

```bash
uv run --no-sync python -m modules.topic.route "<arguments>"
```

Switching auto-saves any chat active in the outgoing topic first — see the `chat` skill for the
`/chat` commands that operate inside whichever topic is currently active.
