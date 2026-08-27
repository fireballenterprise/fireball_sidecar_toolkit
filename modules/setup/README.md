# Setup Module
One-time repo bootstrapping helpers, called by `setup.sh`.

## Commands
```sh
uv run --no-sync invoke setup.properties
```

## What It Does
`properties.yml` is gitignored **only in template repos** (this one and its siblings — anything
named `template_*`), since it would otherwise leak this machine's local paths into the template's
own history. In a real repo forked from a template, setup strips the ignore line from `.gitignore`
the first time it runs there, so `properties.yml` is committed like any other repo config — see
`_sync_gitignore_tracking()`. Creating the file itself is **a no-op if it already exists** —
`modules/setup/properties.py` only ever creates the file, it never rewrites an existing one (the
gitignore check still runs every time, though). To regenerate the file (e.g. after moving the repo,
renaming it, or pointing it at a new fork), delete or rename `properties.yml` first, then run again.

On first run, assembles it from every tier fragment under `modules/setup/templates/properties/*.yml`
— one file per repo in the lineage, each named after itself. This repo (template_python) is the
root: its own fragment, `template_python.yml`, holds just `repo`, `template`, and its own `repos`
entry (no lineage edge, since it has no parent). Descendant repos add their own same-named fragment
on top when they fork from this template or a domain template descended from it.

`repos` (the GitHub org/repo map + template lineage) is built additively rather than concatenated:
each fragment's own `repos:` block contributes just its own org/repo + the lineage edge to its
parent, deep-merged into whatever was inherited from earlier tiers. A repo only ever ends up
knowing its own ancestor chain, never a sibling branch it isn't descended from.

Detects this repo's actual path on disk and its git `origin` remote (if any), and stamps
`repo.local`, `repo.remote`, and `screenshots.location` (if a `screenshots` section is present —
generic to that section, not something this root repo declares) with those values. Auto-detects
`template.*` (the parent template repo for `/template`) via GitHub's generated-from link, falling
back to an interactive prompt.

## Files
- `properties.py` — creates `properties.yml` (used by `inv setup.properties`)
- `templates/properties/*.yml` — per-tier fragments merged into a fresh `properties.yml`
- `README.md` — this file
