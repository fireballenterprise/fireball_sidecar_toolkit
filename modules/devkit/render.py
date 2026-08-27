"""Run every renderer over a content bundle and report the files written."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .content import ContentBundle, load_bundle, packaged_content_root
from .renderers import ALL


@dataclass(frozen=True)
class RenderResult:
    written: list[Path]

    @property
    def by_count(self) -> int:
        return len(self.written)


def render_repo(
    repo_root: Path,
    *,
    canonical_root: Path | None = None,
    only: list[str] | None = None,
) -> RenderResult:
    """Regenerate every provider view in ``repo_root`` from canonical content + ``_local/``.

    Args:
        repo_root: consuming repo root.
        canonical_root: override the packaged ``content/`` tree (tests / this repo itself).
        only: restrict to a subset of renderer names (``renderers.ALL`` keys).
    """
    repo_root = repo_root.resolve()
    bundle: ContentBundle = load_bundle(
        canonical_root=canonical_root or packaged_content_root(),
        local_root=repo_root / "_local",
    )

    names = only or list(ALL)
    written: list[Path] = []
    for name in names:
        written.extend(ALL[name](bundle, repo_root))
    return RenderResult(written=sorted(set(written)))
