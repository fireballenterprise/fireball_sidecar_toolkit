"""``sidecar.toolkit.release`` — promote ``development`` -> ``main`` and cut a tagged release.

This task runs **in the toolkit repo itself** (and, once the tasks are shared, from any consuming
repo as a convenience wrapper that just triggers the toolkit's release workflow).

Branch model:
* ``development`` — integration branch. Feature PRs merge here. Consuming repos opt into the dev
  channel by pinning ``fireball-sidecar-toolkit @ git+...@development``.
* ``main`` — stable. Only ever updated by promoting ``development``. Consuming repos pin the
  floating major tag (``@1``) which always points at the latest ``1.x.x`` release commit on
  ``main`` (per Levon's versioning convention: no ``v`` prefix, start at ``1.0.0``).

Steps:
1. Ensure ``development`` is green and ahead of ``main``.
2. Open (or fast-forward) a ``development`` -> ``main`` PR.
3. On merge: bump ``VERSION``, tag the exact version + move the floating major tag, and let the
   release workflow build + publish (GitHub release now; PyPI later, once workflows are live —
   targeted after 2026-09-01).
"""

from __future__ import annotations

from pathlib import Path


def release(repo_root: Path, *, part: str = "patch") -> str:  # noqa: ARG001
    """Promote development -> main and cut a release; return the release URL/tag."""
    raise NotImplementedError("release — see module docstring and the plan's branch model")
