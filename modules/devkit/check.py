"""``devkit check`` — read-only drift gate for ``invoke fix`` / ``invoke test`` and CI.

Re-renders every provider view into memory and compares against what is on disk. Exits non-zero
(raises :class:`DriftError`) on the first mismatch, naming the stale file and the command to fix
it. Never writes.
"""

from __future__ import annotations

from pathlib import Path


class DriftError(RuntimeError):
    """A generated provider file is stale relative to canonical content + ``_local/``."""


def check(repo_root: Path) -> None:  # noqa: ARG001
    """Raise :class:`DriftError` if any generated file is out of date."""
    raise NotImplementedError("check — see module docstring")
