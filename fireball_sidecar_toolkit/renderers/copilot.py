"""Render GitHub Copilot / VS Code files.

* ``.github/instructions/<slug>.instructions.md`` — the materialised instruction: ``description`` +
  ``applyTo`` frontmatter and the canonical body verbatim. Copilot is the one tool that honours
  path-scoped ``applyTo`` auto-loading, so these carry the full text, not a pointer.
* ``.github/copilot-instructions.md`` — the always-on index pointing at the set.
* ``.github/skills/<name>/SKILL.md`` — canonical skill dirs copied verbatim.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, clean_subdirs, copy_tree, write_doc

_INDEX = """# Copilot Instructions

All rules and standards for this repo live under `.github/instructions/` — never duplicate them
here. Start with `.github/instructions/index.instructions.md` for project structure and
conventions, and `.github/instructions/review.instructions.md` when reviewing a pull request.
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
        written.extend(copy_tree(skill.root, skills_dir / skill.name))
    clean_subdirs(skills_dir, [s.name for s in bundle.skills])

    return written
