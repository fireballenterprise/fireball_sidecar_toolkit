"""``sidecar-toolkit sync`` — the smart wrapper ``/toolkit_sync`` and the skill call.

The AI does the asking; this module only reports state and runs the primitive the caller chooses:

1. :func:`inspect` — is ``_shared/`` modified vs the last commit? Returns the diff so the caller can
   ask "upload these first, or discard?".
2. :func:`run` — once resolved: ``download(force=True)`` (clobber ``_shared/`` + regenerate).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._git import dirty_tracked, tracked_diff
from .download import SHARED_DIRNAME, download
from .render import RenderResult


@dataclass(frozen=True)
class SyncPlan:
    dirty: bool
    shared_diff: str
    message: str


def inspect(repo_root: Path) -> SyncPlan:
    """Report whether ``_shared/`` has uncommitted edits, without changing anything."""
    repo_root = repo_root.resolve()
    status = dirty_tracked(repo_root, SHARED_DIRNAME)
    if not status:
        return SyncPlan(
            dirty=False,
            shared_diff="",
            message=f"{SHARED_DIRNAME}/ is clean — safe to `invoke sidecar.toolkit.download`.",
        )
    diff = tracked_diff(repo_root, SHARED_DIRNAME)
    return SyncPlan(
        dirty=True,
        shared_diff=diff,
        message=(
            f"{SHARED_DIRNAME}/ has uncommitted edits:\n{status}\n\n"
            "Upload them to the toolkit first (`invoke sidecar.toolkit.upload`) or discard them, "
            "then download."
        ),
    )


def run(repo_root: Path, *, force: bool = False) -> RenderResult:
    """Clobber ``_shared/`` from the package and regenerate. ``force`` skips the dirty guard."""
    return download(repo_root, force=force)
