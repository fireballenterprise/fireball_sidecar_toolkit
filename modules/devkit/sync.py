"""``devkit sync`` — the smart wrapper ``/devkit_sync`` and the skill call.

Flow (the AI does the asking — this module just reports state and runs the primitive the caller
chooses):

1. Inspect ``_shared/`` for uncommitted modifications vs the packaged canonical content.
2. If there are edits: return a :class:`SyncPlan` with ``dirty=True`` and the diff so the caller
   can ask "upload these first, or discard?".
3. Otherwise (or once the caller resolves it): :mod:`modules.devkit.download` then the drift
   check.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncPlan:
    dirty: bool
    shared_diff: str
    message: str


def inspect(repo_root: Path) -> SyncPlan:  # noqa: ARG001
    """Report whether ``_shared/`` diverges from canonical, without changing anything."""
    raise NotImplementedError("sync.inspect — see module docstring")
