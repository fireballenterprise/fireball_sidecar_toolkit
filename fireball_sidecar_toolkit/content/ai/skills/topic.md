---
name: topic
description: Use for switching the active planning-topic workspace, or listing/creating/initializing/reindexing/updating topics under topics/. Equivalent to /topic.
---

# Topic Workspace Workflow
Use this file as source of truth: `.ai/toolkit/commands/topic.md`

When the user asks to switch topics, list topics, create a new topic, or run a `/topic`
equivalent, read that file and follow it.

- Switch: `switch <path>` (or bare `<path>`) — paths nest to any depth; a switch to an
  unregistered-but-real topic dir self-heals the index for that path
- List: `list` (active only) / `list all` (full tree, active starred)
- Create: `new <path> [description] [--instructions=a,b]`
- Initialize in place: `init [description] [--instructions=a,b]`
- Rebuild `topics_list.yml` from the directories on disk: `reindex [--dry-run]`
- Regenerate AGENTS.md/CLAUDE.md from template + `topic_meta`: `update [--dry-run] [--current-only] [--topic=a,b]`

Run the router from the repo root:

```bash
uv run --no-sync python -m modules.toolkit.topic.route "<arguments>"
```

Switching auto-saves any chat active in the outgoing topic first — see the `chat` skill for the
`/chat` commands that operate inside whichever topic is currently active.
