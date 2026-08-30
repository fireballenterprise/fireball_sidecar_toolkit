"""Render ``.sidecar/`` for Fireball Sidecar — pointer stubs.

``commands/``, ``instructions/``, ``skills/`` each carry the provider frontmatter Sidecar needs
and a one-line pointer at the canonical ``.ai/toolkit/`` or ``.ai/<repo>/`` file. Sidecar is Levon's
own tool and is being taught to read the canonical ``.ai/`` tree directly; the target end state is
a no-op renderer.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import canonical_pointer, clean_dir, write_doc

_AGENT = "sidecar-agent"


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    root = repo_root / ".sidecar"
    written: list[Path] = []

    cmd_dir = root / "commands"
    cmd_files = [
        write_doc(
            cmd_dir / f"{c.slug}.md",
            canonical_pointer(bundle, c.slug, "commands"),
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
            canonical_pointer(bundle, i.slug, "instructions"),
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
                canonical_pointer(bundle, skill.name, "skills"),
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
