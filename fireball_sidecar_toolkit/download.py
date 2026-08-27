"""``sidecar-toolkit download`` — clobber ``_shared/`` from the installed package, then regenerate.

Steps:
1. Refuse to run if ``_shared/`` has uncommitted local modifications (caller should route through
   :mod:`fireball_sidecar_toolkit.sync`, which asks the user what to do).
2. ``rm -rf _shared/`` and copy the packaged ``content/`` tree into it verbatim.
3. :func:`fireball_sidecar_toolkit.render.render_repo` to rewrite every provider view.
4. :mod:`fireball_sidecar_toolkit.check` for the drift gate.
"""

from __future__ import annotations

from pathlib import Path

from .render import RenderResult

SHARED_DIRNAME = "_shared"


def download(repo_root: Path, *, force: bool = False) -> RenderResult:  # noqa: ARG001
    """Clobber ``_shared/`` from the packaged canonical tree, then render every provider view.

    Implementation lands in the next pass: guard on a dirty ``_shared/`` unless ``force``,
    ``rm -rf`` + copy from :func:`fireball_sidecar_toolkit.catalog.packaged_content_root`, then
    :func:`fireball_sidecar_toolkit.render.render_repo`.
    """
    raise NotImplementedError("download — see DESIGN.md and module docstring")
