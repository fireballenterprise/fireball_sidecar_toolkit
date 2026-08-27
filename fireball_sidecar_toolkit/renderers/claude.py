"""Render ``.claude/commands/*.md`` and ``.claude/skills/`` for Claude Code.

Claude Code uses the filename as the command name and reads only ``description`` from frontmatter;
extra keys are ignored. Command body is the canonical body verbatim (including the ``!`...``` exec
line). Skills are copied directory-for-directory from the bundle.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("claude renderer — see DESIGN.md")
