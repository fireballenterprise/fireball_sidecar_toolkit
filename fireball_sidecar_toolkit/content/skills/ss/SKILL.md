---
name: ss
description: Use for viewing the latest screenshot from the centralized screenshots/ folder. Equivalent to /ss.
---

# Screenshot View Workflow

Use this file as source of truth: `.github/prompts/ss.prompt.md`

When the user asks to look at the latest screenshot, or runs a `/ss` equivalent, read that prompt
file and follow it.

```bash
uv run --no-sync python -m modules.repo.route "view_screenshot"
```

Then use the `view_image` tool on `screenshots/latest.png` (relative to the repo root). See
`.github/instructions/screenshots.instructions.md` for the shared-folder rules.
