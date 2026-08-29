"""Render GitHub Copilot / VS Code files.

* ``.github/instructions/<slug>.instructions.md`` — the materialised instruction: ``description`` +
  ``applyTo`` frontmatter and the canonical body verbatim. Copilot is the one tool that honours
  path-scoped ``applyTo`` auto-loading, so these carry the full text, not a pointer.
* ``.github/copilot-instructions.md`` — the always-on index pointing at the set.
* ``.github/skills/<name>/SKILL.md`` — the flat canonical skill file wrapped in the ``<name>/SKILL.md``
  shape Copilot requires.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, clean_subdirs, write_doc

_INDEX = """# Copilot Instructions

See `AGENTS.md` at the repo root for the project overview, the instruction-file map, and the
golden rules. Domain rules live under `.github/instructions/*.instructions.md` and auto-apply by
their `applyTo` glob. Never duplicate rules into this file.
"""


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    github = repo_root / ".github"

    inst_dir = github / "instructions"
    written = [
        write_doc(
            inst_dir / f"{i.slug}.instructions.md",
            i.body,
            frontmatter={"description": i.description, "applyTo": i.apply_to},
        )
        for i in bundle.instructions
    ]
    clean_dir(inst_dir, written)

    written.append(write_doc(github / "copilot-instructions.md", _INDEX))

    skills_dir = github / "skills"
    for skill in bundle.skills:
        frontmatter, body = skill.read()
        written.append(
            write_doc(
                skills_dir / skill.name / "SKILL.md",
                body,
                frontmatter={
                    "name": skill.name,
                    "description": str(frontmatter.get("description", "")),
                    "hints": frontmatter.get("hints") or (),
                },
            )
        )
    clean_subdirs(skills_dir, [s.name for s in bundle.skills])

    return written
