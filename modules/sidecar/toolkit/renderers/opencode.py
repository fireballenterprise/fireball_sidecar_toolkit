"""Render ``.opencode/command/*.md`` for OpenCode.

Frontmatter: ``description``, ``agent: general``, ``subtask: false`` (prevents Task-tool
recursion), ``slash_command: /<slug>``. Body is the canonical body with the inline ``!`...```
exec line kept as-is. Folds in the logic currently in ai_vault's ``modules/opencode/sync.py``.
"""

from __future__ import annotations

from pathlib import Path

from ..content import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("opencode renderer — see DESIGN.md")
