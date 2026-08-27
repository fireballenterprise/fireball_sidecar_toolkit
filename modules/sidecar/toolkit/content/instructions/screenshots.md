---
applyTo: "**"
---
# Screenshots Instructions
Rules for working with the `screenshots/` folder at the repository root.

## Purpose
`screenshots/` is the **single shared folder for all screenshots across the entire repository**. All topics share it — no topic-specific screenshots folders exist.

Git LFS tracks: `*.png`, `*.jpg`, `*.svg`

## Rules
- **NEVER create a `screenshots/` subfolder inside a topic directory** — screenshots always go to the repo-root `screenshots/` folder
- `latest.png` is a working file — it is the most recently copied screenshot, used as a scratch file for AI tools to read
- Do not reference screenshots by absolute path — use paths relative to the repo root (e.g. `screenshots/latest.png`)

## Commands

| Command | What it does |
|---------|-------------|
| `/repo view_screenshot` (alias `/ss`) | Copies the latest macOS screenshot to `screenshots/latest.png` for AI viewing |
| `/repo set_screenshots` | Configures macOS to save screenshots to the `screenshots/` folder |
| `/repo cleanup` | Deletes all screenshot images from `screenshots/` to free space |

## Viewing a Screenshot
When the user shares a screenshot or asks you to look at one:

1. The user runs `/ss` (or `/repo view_screenshot`) to copy the latest screenshot to `screenshots/latest.png`
2. Use `view_image` on `screenshots/latest.png` to read it
3. Treat the image contents as context for the current conversation — do not auto-create a doc unless asked

## Module Implementation
For implementation details and command internals, see `modules/repo/README.md`.
