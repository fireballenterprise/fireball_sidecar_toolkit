"""Render ``.github/prompts/*.prompt.md`` (GitHub.com prompt-file UI + legacy compatibility).

Frontmatter: ``name``, ``description``, ``argument-hint``, ``agent``. Body is the canonical body
verbatim. This was the historical source of truth; it is now just another generated view kept for
the github.com prompt picker.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("prompts renderer — see DESIGN.md")
