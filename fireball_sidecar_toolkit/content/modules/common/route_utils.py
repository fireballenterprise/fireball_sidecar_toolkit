"""Shared helpers for AI-tool command routing modules."""

from __future__ import annotations

import logging
import os
from pathlib import Path

LOGGER = logging.getLogger(__name__)


#: Set this to run a routed command against a different checkout than the current directory's
#: (e.g. a wrapper that targets another managed repo). find_repo_root() honours it before searching.
REPO_ROOT_ENV = "SIDECAR_REPO_ROOT"


def find_repo_root() -> Path:
    """Return the repo root: ``$SIDECAR_REPO_ROOT`` if set, else the nearest parent with properties.yml."""
    override = os.environ.get(REPO_ROOT_ENV)
    if override:
        return Path(override)
    current = Path.cwd()
    while current != current.parent:
        if (current / "properties.yml").exists():
            return current
        current = current.parent
    return Path.cwd()


def build_env(_repo_root: Path) -> dict[str, str]:
    """Build the subprocess environment for a routed command."""
    return os.environ.copy()
