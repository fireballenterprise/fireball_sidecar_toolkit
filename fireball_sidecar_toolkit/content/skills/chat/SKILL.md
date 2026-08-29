---
name: chat
description: Use for starting, ending, listing, or resuming a dated planning chat inside the active topic. Equivalent to /chat.
---

# Chat Session Workflow

Use this file as source of truth: `.github/prompts/chat.prompt.md`

When the user asks to start/end/list/resume a chat, or run a `/chat` equivalent, read that prompt
file and follow it.

- Start: `start [title]`
- List: `list`
- Resume: `resume [pattern]`
- End: `end` (requires the agent to have written a real `## Overview` summary and `## Chat Log`
  entries in the active chat file first — see the prompt for the exact format)

Run the router from the repo root:

```bash
uv run --no-sync python -m modules.chat.route "<arguments>"
```

Operates on whichever topic is currently active — see the `topic` skill for `/topic switch`.
