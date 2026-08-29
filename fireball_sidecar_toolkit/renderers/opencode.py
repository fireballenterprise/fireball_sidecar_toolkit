"""Render ``.opencode/command/*.md`` for OpenCode.

Frontmatter: ``description``, ``agent: general``, ``subtask: false`` (blocks Task-tool recursion),
``slash_command: /<slug>``. Body is the canonical body verbatim, inline ``!`...``` exec line kept.
Supersedes ai_vault's ``modules/opencode/sync.py``.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, write_doc


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    out_dir = repo_root / ".opencode" / "command"
    written = [
        write_doc(
            out_dir / f"{command.slug}.md",
            command.body,
            frontmatter={
                "description": command.description,
                "agent": "general",
                "subtask": "false",
                "slash_command": f"/{command.slug}",
            },
        )
        for command in bundle.commands
    ]
    clean_dir(out_dir, written)
    return written
