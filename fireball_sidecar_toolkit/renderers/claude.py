"""Render Claude Code files.

* ``.claude/commands/<slug>.md`` — canonical body verbatim (inline ``!`...``` exec line included)
  under Claude-specific frontmatter: ``description``, ``subtask: false``, ``agent: general``,
  ``slash_command: /<slug>``, and an ``allowed-tools`` glob derived from the exec line
  (:func:`~fireball_sidecar_toolkit.renderers._common.derive_allowed_tools`) so the command runs
  without a permission prompt. These extras are a template pattern, not stored per canonical file.
* ``.claude/skills/<name>/`` — canonical skill dirs copied verbatim.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, clean_subdirs, copy_tree, derive_allowed_tools, write_doc


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    claude = repo_root / ".claude"

    cmd_dir = claude / "commands"
    written: list[Path] = []
    for command in bundle.commands:
        allowed = derive_allowed_tools(command)
        written.append(
            write_doc(
                cmd_dir / f"{command.slug}.md",
                command.body,
                frontmatter={
                    "description": command.description,
                    "subtask": "false",
                    "agent": "general",
                    "slash_command": f"/{command.slug}",
                    "allowed-tools": ", ".join(allowed),
                },
            )
        )
    clean_dir(cmd_dir, written)

    skills_dir = claude / "skills"
    for skill in bundle.skills:
        written.extend(copy_tree(skill.root, skills_dir / skill.name))
    clean_subdirs(skills_dir, [s.name for s in bundle.skills])

    return written
