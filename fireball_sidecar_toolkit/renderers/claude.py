"""Render Claude Code files — all pointer stubs.

* ``.claude/commands/<slug>.md`` — Claude-specific frontmatter (``description``, ``subtask: false``,
  ``agent: general``, ``slash_command: /<slug>``, and an ``allowed-tools`` glob still derived from
  the canonical body's ``!`...``` exec line so the command runs without a permission prompt), body
  a one-line pointer at ``.ai/shared|local/commands/<slug>.md``.
* ``.claude/skills/<name>/SKILL.md`` — ``name``/``description``/``hints`` frontmatter in the
  ``<name>/SKILL.md`` shape Claude Code requires, body a pointer at
  ``.ai/shared|local/skills/<name>.md``.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import canonical_pointer, clean_dir, clean_subdirs, derive_allowed_tools, write_doc


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    claude = repo_root / ".claude"

    cmd_dir = claude / "commands"
    written: list[Path] = []
    for command in bundle.commands:
        allowed = derive_allowed_tools(command)
        written.append(
            write_doc(
                cmd_dir / f"{command.slug}.md",
                canonical_pointer(bundle, command.slug, "commands"),
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
        frontmatter, _ = skill.read()
        written.append(
            write_doc(
                skills_dir / skill.name / "SKILL.md",
                canonical_pointer(bundle, skill.name, "skills"),
                frontmatter={
                    "name": skill.name,
                    "description": str(frontmatter.get("description", "")),
                    "hints": frontmatter.get("hints") or (),
                },
            )
        )
    clean_subdirs(skills_dir, [s.name for s in bundle.skills])

    return written
