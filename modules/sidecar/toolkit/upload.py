"""``sidecar-toolkit upload`` — promote local ``_shared/`` edits back to fireball_sidecar_toolkit as a PR.

Steps:
1. Diff the repo's ``_shared/`` against the packaged canonical ``content/``.
2. Refuse if the diff touches anything outside ``_shared/`` (never carries ``_local/`` or
   generated provider files).
3. Clone / worktree fireball_sidecar_toolkit, apply the diff onto a new branch, push, open a PR with ``gh``.
   Never a direct push to ``fireball_sidecar_toolkit`` ``main``.
"""

from __future__ import annotations

from pathlib import Path


def upload(repo_root: Path, *, branch: str | None = None) -> str:  # noqa: ARG001
    """Open a PR against fireball_sidecar_toolkit with this repo's ``_shared/`` changes; return the PR URL."""
    raise NotImplementedError("upload — see DESIGN.md and module docstring")
