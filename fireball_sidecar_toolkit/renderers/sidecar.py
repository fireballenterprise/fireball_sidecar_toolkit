"""Render ``.sidecar/`` for Fireball Sidecar.

Interim state: thin pointer stubs (``commands/``, ``instructions/``, ``skills/``) back to the
materialised ``.github/`` files, matching the pattern already used across the family. Target end
state is a **no-op** — Sidecar is Levon's own tool and is being taught to read the canonical files
(``AGENTS.md`` + ``.github/instructions/`` honouring ``applyTo``, ``.github/prompts/``) directly.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, write_doc

_AGENT = "sidecar-agent"


def _pointer(target: str) -> str:
    return f"Use this file as source of truth: {target}"


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    root = repo_root / ".sidecar"
    written: list[Path] = []

    cmd_dir = root / "commands"
    cmd_files = [
        write_doc(
            cmd_dir / f"{c.slug}.md",
            _pointer(f".github/prompts/{c.slug}.prompt.md"),
            frontmatter={
                "name": c.slug,
                "description": c.description,
                "argument-hint": c.argument_hint,
                "agent": _AGENT,
            },
        )
        for c in bundle.commands
    ]
    clean_dir(cmd_dir, cmd_files)
    written += cmd_files

    inst_dir = root / "instructions"
    inst_files = [
        write_doc(
            inst_dir / f"{i.slug}.md",
            _pointer(f".github/instructions/{i.slug}.instructions.md"),
            frontmatter={"name": i.slug, "description": i.description, "applyTo": i.apply_to},
        )
        for i in bundle.instructions
    ]
    clean_dir(inst_dir, inst_files)
    written += inst_files

    skill_dir = root / "skills"
    skill_files = []
    for skill in bundle.skills:
        frontmatter, _ = skill.read()
        skill_files.append(
            write_doc(
                skill_dir / f"{skill.name}.md",
                _pointer(f".github/skills/{skill.name}/SKILL.md"),
                frontmatter={
                    "name": skill.name,
                    "description": str(frontmatter.get("description", "")),
                    "hints": frontmatter.get("hints") or (),
                },
            )
        )
    clean_dir(skill_dir, skill_files)
    written += skill_files

    return written
