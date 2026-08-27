"""Render ``.sidecar/`` for Fireball Sidecar.

Target end state: a **no-op**. Sidecar is Levon's own tool, so it is being taught to read the
canonical files directly — ``AGENTS.md`` + ``_shared/instructions/`` (honoring ``applyTo``) and
``_shared/commands/`` — rather than consuming a generated mirror.

Interim: emit ``.sidecar/commands/<slug>.md`` pointer stubs
(``Use this file as source of truth: _shared/commands/<slug>.md``), matching the pattern already
in ai_vault, until Sidecar's native reader lands.
"""

from __future__ import annotations

from pathlib import Path

from ..content import ContentBundle


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:  # noqa: ARG001
    raise NotImplementedError("sidecar renderer — see DESIGN.md (interim pointer stubs)")
