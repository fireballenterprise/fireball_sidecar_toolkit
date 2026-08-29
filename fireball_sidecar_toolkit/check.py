"""``sidecar-toolkit check`` — read-only drift gate for ``invoke test`` and CI.

Two invariants, checked without writing anything:

1. ``_shared/`` byte-matches the packaged canonical ``content/`` tree.
2. Every generated provider file byte-matches a fresh render of ``content/`` + ``_local/``.

Raises :class:`DriftError` naming the stale paths and the command to fix them.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .catalog import packaged_content_root
from .render import render_repo


class DriftError(RuntimeError):
    """A generated provider file (or ``_shared/``) is stale relative to canonical content."""


def _tree_mismatches(expected: Path, actual: Path, *, label: str) -> list[str]:
    if not actual.is_dir():
        return [f"{label}/ (missing — run `invoke sidecar.toolkit.download`)"]
    out: list[str] = []
    expected_files = {p.relative_to(expected) for p in expected.rglob("*") if p.is_file()}
    actual_files = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()}
    for rel in sorted(expected_files - actual_files):
        out.append(f"{label}/{rel} (missing)")
    for rel in sorted(actual_files - expected_files):
        out.append(f"{label}/{rel} (stale, not in canonical)")
    for rel in sorted(expected_files & actual_files):
        if (expected / rel).read_bytes() != (actual / rel).read_bytes():
            out.append(f"{label}/{rel}")
    return out


def check(repo_root: Path) -> None:
    """Raise :class:`DriftError` if any generated file — or ``_shared/`` — is out of date."""
    repo_root = repo_root.resolve()
    packaged = packaged_content_root()

    stale = _tree_mismatches(packaged, repo_root / "_shared", label="_shared")

    with tempfile.TemporaryDirectory() as tmp:
        mirror = Path(tmp).resolve()
        local = repo_root / "_local"
        if local.is_dir():
            shutil.copytree(local, mirror / "_local")
        for produced in render_repo(mirror, canonical_root=packaged).written:
            rel = produced.relative_to(mirror)
            on_disk = repo_root / rel
            if not on_disk.is_file():
                stale.append(f"{rel} (missing)")
            elif on_disk.read_bytes() != produced.read_bytes():
                stale.append(str(rel))

    if stale:
        raise DriftError(
            "Generated AI-provider files are stale:\n  - "
            + "\n  - ".join(stale)
            + "\nRun `invoke sidecar.toolkit.sync` (or `download`) to regenerate."
        )
