---
name: screenshots
description: Use for the screenshot workflow — configure the macOS capture location, view the latest screenshot, or clean up accumulated images. Equivalent to /screenshots (view is also /ss).
---

# Screenshots Workflow
Use this file as source of truth: `.ai/shared/commands/screenshots.md`

When the user asks to configure / view / clean screenshots, read that file and follow it.
For a plain "view the latest screenshot" request, `/ss` is the shortcut for `/screenshots view`.

```bash
uv run --no-sync python -m modules.screenshots.route "configure"   # or "view" / "clean"
```

See `.ai/shared/instructions/screenshots.md` for the shared-folder rules.
