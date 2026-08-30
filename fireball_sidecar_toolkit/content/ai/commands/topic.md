---
name: topic
description: Switch topics, list the active topic, or show all topics
argument-hint: list [all] | switch <path> | new <path> [description] | init [description] | update [--dry-run]
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.topic.route "$ARGUMENTS"`


If $ARGUMENTS starts with "new", create a new topic at the given path (relative to topics/), then run init in that directory. Example: /topic new workshop/3d_printing [description].

If $ARGUMENTS starts with "list all", render the command output as a tree showing all topics and subtopics. Mark the active topic with ⭐. End with a one-line summary.

If $ARGUMENTS starts with "list" and does not include "all", show the active topic only and mention that "list all" reveals the full topic tree.

After running the command, if the output shows a topic switch (contains "Switched to:"):
- The **Full path** line in the output is now the active topic root for this conversation
- ALL subsequent relative paths resolve under that full path:
  - `docs/...` → `{topic_full_path}/docs/...`
  - `2026/...` → `{topic_full_path}/2026/...`
  - Any bare filename/folder → `{topic_full_path}/...`
- Do NOT use any previously cached topic path — the new path from this output is the source of truth
- Do NOT read `active_topic.yml` to determine the path; use the command output directly
