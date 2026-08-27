"""Render ``.github/copilot-instructions.md`` and ``.github/instructions/*.instructions.md``.

GitHub Copilot / VS Code reads ``.github/instructions/<slug>.instructions.md`` with an ``applyTo``
glob in frontmatter (the one tool that honors path-scoped instructions). Each canonical
instruction maps 1:1, keeping its ``description`` + ``applyTo``. ``copilot-instructions.md`` is a
short always-on index pointing at the set.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("copilot renderer — see DESIGN.md")
