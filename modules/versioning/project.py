"""Bump the repo's VERSION file (PEP 440 ``Major.Minor.Patch``).

VERSION is the single source of truth — ``pyproject.toml`` reads it via
``[tool.setuptools.dynamic]``. It is always a plain ``X.Y.Z`` on ``development`` and ``main``:

* every PR merge to ``development`` -> ``ver.project_bump_patch``  (``0.2.0`` -> ``0.2.1``)
* each release -> ``ver.project_bump_minor`` (default) or ``_major`` for a milestone
  (``0.2.7`` -> ``0.3.0``; the eventual official launch dispatches ``bump=major`` -> ``1.0.0``)

``ver.project_bump_build`` (``X.Y.Z`` -> ``X.Y.Z-001`` -> ``-002``) stays available for manual
use on a feature branch; nothing published ever carries a build suffix.

Usage:
    uv run --no-sync invoke ver.project_bump_patch
    uv run --no-sync invoke ver.project_bump_minor
    uv run --no-sync invoke ver.project_bump_major
    uv run --no-sync invoke ver.project_bump_build
"""

from __future__ import annotations

import re
from pathlib import Path

from ..common.properties import get_repo_root
from ..common.utils import error, success

_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-(\d+))?$")
_BUILD_WIDTH = 3


def _version_file(repo_root: Path) -> Path:
    return repo_root / "VERSION"


def _read(repo_root: Path) -> tuple[int, int, int, int | None]:
    version_file = _version_file(repo_root)
    if not version_file.is_file():
        error(f"VERSION file not found at {version_file}")
    raw = version_file.read_text(encoding="utf-8").strip()
    match = _VERSION_PATTERN.match(raw)
    if not match:
        error(f"VERSION contents {raw!r} don't match Major.Minor.Patch[-Build]")
    major, minor, patch, build = match.groups()
    return int(major), int(minor), int(patch), int(build) if build else None


def _write(repo_root: Path, version: str) -> str:
    _version_file(repo_root).write_text(f"{version}\n", encoding="utf-8")
    success(f"VERSION set to {version}")
    return version


def bump_patch() -> str:
    """``X.Y.Z[-B]`` -> ``X.Y.(Z+1)``. Every PR merge to development."""
    repo_root = get_repo_root()
    major, minor, patch, _ = _read(repo_root)
    return _write(repo_root, f"{major}.{minor}.{patch + 1}")


def bump_minor() -> str:
    """``X.Y.Z[-B]`` -> ``X.(Y+1).0``. The default release bump."""
    repo_root = get_repo_root()
    major, minor, _patch, _ = _read(repo_root)
    return _write(repo_root, f"{major}.{minor + 1}.0")


def bump_major() -> str:
    """``X.Y.Z[-B]`` -> ``(X+1).0.0``. Milestone releases (e.g. the official 1.0.0)."""
    repo_root = get_repo_root()
    major, _minor, _patch, _ = _read(repo_root)
    return _write(repo_root, f"{major + 1}.0.0")


def bump_build() -> str:
    """``X.Y.Z`` -> ``X.Y.Z-001``; ``X.Y.Z-NNN`` -> ``X.Y.Z-(NNN+1)``. Manual, feature-branch only."""
    repo_root = get_repo_root()
    major, minor, patch, build = _read(repo_root)
    next_build = 1 if build is None else build + 1
    return _write(repo_root, f"{major}.{minor}.{patch}-{next_build:0{_BUILD_WIDTH}d}")


if __name__ == "__main__":
    bump_patch()
