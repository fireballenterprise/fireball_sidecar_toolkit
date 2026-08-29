"""``sidecar-toolkit download`` — clobber ``ai/shared/`` from the installed package, then regenerate.

1. Refuse if ``ai/shared/`` has uncommitted local modifications (unless ``force``) — the caller
   should route through :mod:`fireball_sidecar_toolkit.sync`, which asks the user what to do.
2. ``rm -rf ai/shared/`` and copy the packaged ``content/`` tree into it verbatim.
3. :func:`fireball_sidecar_toolkit.render.render_repo` to rewrite every provider view.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ._git import dirty_tracked
from .catalog import packaged_content_root
from .render import RenderResult, render_repo

SHARED_SUBPATH = "ai/shared"


class DirtySharedError(RuntimeError):
    """``ai/shared/`` has uncommitted edits — resolve them (upload or discard) before a clobber."""


def clobber_shared(repo_root: Path, *, force: bool = False) -> Path:
    """Replace ``repo_root/ai/shared`` with a fresh copy of the packaged ``content/`` tree."""
    shared = repo_root / SHARED_SUBPATH
    if not force and dirty_tracked(repo_root, SHARED_SUBPATH):
        raise DirtySharedError(
            f"{SHARED_SUBPATH}/ has uncommitted changes. Run `invoke sidecar.toolkit.sync` to "
            "upload or discard them first, or pass force=True."
        )
    if shared.exists():
        shutil.rmtree(shared)
    shutil.copytree(packaged_content_root(), shared)
    return shared


def download(repo_root: Path, *, force: bool = False) -> RenderResult:
    """Clobber ``ai/shared/`` from the packaged canonical tree, then render every provider view."""
    repo_root = repo_root.resolve()
    shared = clobber_shared(repo_root, force=force)
    return render_repo(repo_root, canonical_root=shared)
