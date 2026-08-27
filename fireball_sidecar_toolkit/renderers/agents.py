"""Render ``AGENTS.md`` (+ thin ``CLAUDE.md`` pointer) from the instruction bundle.

``AGENTS.md`` is the primary, tool-neutral instruction file — the convergence point Codex,
Cursor, Copilot and others already read. It concatenates every instruction body under a short
generated preamble. ``CLAUDE.md`` is a one-line ``@AGENTS.md`` pointer so Claude Code inherits the
same content without a second copy.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("agents renderer — see DESIGN.md")
