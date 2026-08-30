"""``sidecar-toolkit download`` — clobber every shipped tree from the installed package, then render.

Everything under the package's ``content/`` is copied verbatim into the consuming repo:

* ``content/ai/``       → ``.ai/toolkit/`` (then rendered into every provider dir)
* ``content/modules/``  → ``modules/toolkit/``  (shared Python, imported as ``modules.toolkit.*``)
* ``content/tasks/``    → ``tasks/toolkit/``
* ``content/tests/``    → ``tests/toolkit/``
* ``content/scripts/setup.sh`` / ``setup.ps1`` → repo root

Refuses if any of those paths has uncommitted local modifications (unless ``force``) — the caller
should route through :mod:`fireball_sidecar_toolkit.sync`, which asks the user what to do.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ._git import dirty_tracked
from .catalog import CLOBBER_TREES, packaged_content_root, read_vendor, vendored_files, vendored_trees
from .render import RenderResult, render_repo

TOOLKIT_SUBPATH = CLOBBER_TREES["ai"]  # ".ai/toolkit" — kept as a name for back-compat imports


class DirtySharedError(RuntimeError):
    """A clobbered path has uncommitted edits — resolve them (upload or discard) before a clobber."""


def _ignore_pycache(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n == "__pycache__" or n.endswith((".pyc", ".pyo"))}


def clobber_shared(repo_root: Path, *, force: bool = False) -> Path:
    """Replace every clobbered tree/file in ``repo_root`` with a fresh copy from the package.

    Honours ``.sidecar-toolkit.yml`` — a repo that vendors only a subset (e.g. ``[ai, scripts]``)
    keeps its own ``modules/toolkit/`` etc. untouched.
    """
    content = packaged_content_root()
    trees, files = vendored_trees(repo_root), vendored_files(repo_root)
    guarded = (*trees.values(), *files.values())
    if not force:
        dirty = [p for p in guarded if dirty_tracked(repo_root, p)]
        if dirty:
            raise DirtySharedError(
                f"Uncommitted changes in a toolkit-managed path: {', '.join(dirty)}. Run "
                "`invoke sidecar.toolkit.sync` to upload or discard them first, or pass force=True."
            )

    for key, rel in trees.items():
        src = content / key
        dest = repo_root / rel
        if dest.exists():
            shutil.rmtree(dest)
        if src.is_dir():
            shutil.copytree(src, dest, ignore=_ignore_pycache)

    for src_rel, dest_rel in files.items():
        src = content / src_rel
        if src.is_file():
            dest = repo_root / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if dest.suffix == ".sh":
                dest.chmod(0o755)

    return repo_root / TOOLKIT_SUBPATH


def download(repo_root: Path, *, force: bool = False) -> RenderResult:
    """Clobber every shipped (vendored) tree from the package, then render every provider view.

    A repo that does not vendor ``ai`` (``.sidecar-toolkit.yml``) skips the render step — its
    provider files are its own.
    """
    repo_root = repo_root.resolve()
    ai_root = clobber_shared(repo_root, force=force)
    if "ai" not in read_vendor(repo_root):
        return RenderResult(written=[])
    return render_repo(repo_root, canonical_root=ai_root)
