---
name: ss
description: Use for viewing the latest screenshot from the centralized screenshots/ folder. Equivalent to /ss (which is /screenshots view). Also triggered by "look at my screen", "check this screenshot", or "see my screenshot".
hints:
  - look at my screen
  - check this screenshot
  - see my screenshot
  - look at the screenshot
---

# Screenshot View Workflow

Use this file as source of truth: `.github/prompts/ss.prompt.md`

When the user asks to look at the latest screenshot, or runs a `/ss` equivalent, read that prompt
file and follow it.

```bash
uv run --no-sync python -m modules.screenshots.route "view"
```

Then use the `view_image` tool on `screenshots/latest.png` (relative to the repo root). See
`.github/instructions/screenshots.instructions.md` for the shared-folder rules.
