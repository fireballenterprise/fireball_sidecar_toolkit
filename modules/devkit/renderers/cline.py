"""Render ``.clinerules/workflows/*.md`` for Cline.

Cline workflows are plain-markdown body only — no frontmatter. Cline cannot run inline ``!`...```
execution, so the canonical exec line is rewritten into an explicit "Run this terminal command:"
block wrapping the same command.
"""

from __future__ import annotations

from pathlib import Path

from ..content import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("cline renderer — see DESIGN.md")
