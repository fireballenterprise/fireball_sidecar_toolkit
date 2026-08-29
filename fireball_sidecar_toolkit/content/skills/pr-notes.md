---
name: pr-notes
description: Use for drafting Pull Request notes (Summary + Changes) for the current feature branch against its base branch, without opening a PR. Equivalent to /pr-notes.
---

# PR Notes Workflow

Use this file as source of truth: `.ai/shared/commands/pr-notes.md`

When the user asks to draft PR notes or a PR description, read that file and follow it.

```bash
uv run --no-sync invoke repo.pr_diff
```

Write the description using the canonical `## Summary` / `## Changes` format from
`.ai/shared/instructions/git.md`, then save it:

```bash
uv run --no-sync invoke repo.pr_notes_save --content="<the notes>"
```

If you're running as a step inside another command (e.g. `pr` or `ship-it`), don't save — just
hold the composed notes for that command to use directly.
