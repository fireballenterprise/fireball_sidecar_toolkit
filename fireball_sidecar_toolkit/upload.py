"""``sidecar-toolkit upload`` — promote local ``.ai/shared/`` edits back to the toolkit as a PR.

1. Diff the repo's ``.ai/shared/`` against the packaged canonical ``content/``.
2. Refuse if anything outside ``.ai/shared/`` differs (never carries ``.ai/local/`` or generated files).
3. In a local ``fireball_sidecar_toolkit`` checkout: branch off ``development``, apply the changed
   files into ``content/``, commit, push, open a PR with ``gh``. Never a direct push to ``main``.

The toolkit checkout is resolved in order: an explicit ``toolkit_repo`` arg → the
``FIREBALL_SIDECAR_TOOLKIT_REPO`` env var → a sibling ``../fireball_sidecar_toolkit`` dir.
"""

from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
from pathlib import Path

from ._git import git, is_git_repo
from .catalog import packaged_content_root
from .download import SHARED_SUBPATH

_PACKAGE_NAME = "fireball_sidecar_toolkit"
_REPO_ENV_VAR = "FIREBALL_SIDECAR_TOOLKIT_REPO"


class UploadError(RuntimeError):
    """Preconditions for an upload were not met."""


def _resolve_toolkit(repo_root: Path, override: Path | None) -> Path:
    env = os.environ.get(_REPO_ENV_VAR)
    candidate = (override or (Path(env) if env else repo_root.parent / _PACKAGE_NAME)).expanduser().resolve()
    pyproject = candidate / "pyproject.toml"
    if not pyproject.is_file() or f'name = "{_PACKAGE_NAME}"' not in pyproject.read_text(encoding="utf-8"):
        raise UploadError(
            f"No {_PACKAGE_NAME} checkout at {candidate}. Pass toolkit_repo=... "
            f"or set {_REPO_ENV_VAR}=/path/to/fireball_sidecar_toolkit."
        )
    return candidate


def _changed_files(shared: Path, packaged: Path) -> list[Path]:
    """Relative paths under ``.ai/shared/`` that differ from (or are new vs) the packaged tree."""
    changed: list[Path] = []
    for path in sorted(p for p in shared.rglob("*") if p.is_file()):
        rel = path.relative_to(shared)
        reference = packaged / rel
        if not reference.is_file() or not filecmp.cmp(path, reference, shallow=False):
            changed.append(rel)
    return changed


def upload(repo_root: Path, *, branch: str | None = None, toolkit_repo: Path | None = None) -> str:
    """Open a PR against the toolkit with this repo's ``.ai/shared/`` changes; return the PR URL."""
    repo_root = repo_root.resolve()
    shared = repo_root / SHARED_SUBPATH
    if not shared.is_dir():
        raise UploadError(f"No {SHARED_SUBPATH}/ in {repo_root} — nothing to upload.")

    outside = is_git_repo(repo_root) and git(
        "status", "--porcelain", "--", ".", f":(exclude){SHARED_SUBPATH}", cwd=repo_root, check=False
    )
    if outside:
        raise UploadError(f"Uncommitted changes outside {SHARED_SUBPATH}/ — commit or stash them first.")

    packaged = packaged_content_root()
    changed = _changed_files(shared, packaged)
    if not changed:
        return f"{SHARED_SUBPATH}/ matches canonical content — nothing to upload."

    toolkit = _resolve_toolkit(repo_root, toolkit_repo)
    if git("status", "--porcelain", cwd=toolkit, check=False):
        raise UploadError(f"{toolkit} has uncommitted changes — clean it first.")

    branch = branch or "sync_shared_content"
    git("fetch", "origin", "development", cwd=toolkit)
    git("checkout", "-B", branch, "origin/development", cwd=toolkit)
    for rel in changed:
        target = toolkit / _PACKAGE_NAME / "content" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shared / rel, target)
    git("add", "--", f"{_PACKAGE_NAME}/content", cwd=toolkit)
    summary = ", ".join(str(r) for r in changed)
    git("commit", "-m", f"content: sync from a consuming repo ({summary})", cwd=toolkit)
    git("push", "-u", "origin", branch, cwd=toolkit)

    result = subprocess.run(
        ["gh", "pr", "create", "--base", "development", "--fill"],
        cwd=toolkit,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
