"""``/repo cleanup`` (`/cleanup`) — two phases, in order:

1. **Branch cleanup** — if the current branch has a merged GitHub PR, switch to the default
   branch, pull, delete the branch. Anything that would block that (protected branch, dirty tree,
   no merged PR) is a warning + skip, not a hard error — phase 2 still runs.
2. **Trash sweep** — remove regenerable caches (``__pycache__/``, ``.pytest_cache/``, …) and
   *orphaned* directories under ``modules/`` / ``tasks/`` / ``tests/`` — dirs git tracks no file
   in, the residue a module move (``modules/x`` → ``modules/toolkit/x``) leaves behind. Content
   roots like ``topics/`` and the scratch ``tmp/`` are never touched.

The sweep runs *after* the branch switch + pull on purpose: that's exactly when the leftovers
surface (a file tracked on the old branch/layout becomes untracked once the default branch is in).

Set ``AUTO_CONFIRM=1`` (what ``/repo cleanup all`` does) to skip the sweep prompt. The module
takes no CLI flags — it calls :mod:`pull`'s command entrypoint internally, which can't tolerate
stray argv.
"""

from __future__ import annotations

import fnmatch
import os
import shutil
import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.utils import info, success, warning
from ..setup.properties import get_repo_local
from . import pull as pull_module
from .pr_diff import PROTECTED_BRANCHES, current_branch, detect_base_branch

_CACHE_DIRS = frozenset({"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "htmlcov"})
_CACHE_DIR_GLOBS = ("*.egg-info",)
_CACHE_FILES = frozenset({".DS_Store", ".coverage"})
# Never descend into these — content roots and scratch stay off-limits, and .venv/.git are huge.
_SKIP_DIRS = frozenset({".git", ".venv", "venv", "node_modules", "topics", "tmp"})
_ORPHAN_ROOTS = ("modules", "tasks", "tests")


def _git(args: list[str], repo_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_path, capture_output=True, text=True, check=False)


def _pr_state(repo_path: Path, branch: str) -> str | None:
    """GitHub PR state for ``branch`` (MERGED / OPEN / CLOSED), or None if there's no PR."""
    result = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "state", "-q", ".state"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


# --- phase 1: branch cleanup -----------------------------------------------------------------


def _branch_cleanup(repo_path: Path) -> None:
    branch = current_branch(repo_path)

    if branch in PROTECTED_BRANCHES:
        info(f"Already on '{branch}' — pulling latest, nothing to delete.")
        pull_module.main()
        return

    if _git(["status", "--porcelain"], repo_path).stdout.strip():
        warning(f"Uncommitted changes on '{branch}' — skipping branch cleanup (trash sweep still runs).")
        return

    click.echo(f"🔍 Checking PR status for '{branch}'...")
    state = _pr_state(repo_path, branch)
    if state != "MERGED":
        found = "no PR found" if state is None else f"PR state is {state}"
        warning(f"'{branch}' isn't merged yet ({found}) — skipping branch cleanup.")
        return
    success("PR is merged")

    base_name = detect_base_branch(repo_path, branch).removeprefix("origin/")
    click.echo(f"🔀 Switching to '{base_name}' and pulling...")
    subprocess.run(["git", "checkout", base_name], cwd=repo_path, check=True)
    pull_module.main()
    subprocess.run(["git", "branch", "-D", branch], cwd=repo_path, check=True)
    success(f"Deleted '{branch}' — now on '{base_name}'")


# --- phase 2: trash sweep -------------------------------------------------------------------


def _is_cache_dir(name: str) -> bool:
    return name in _CACHE_DIRS or any(fnmatch.fnmatch(name, glob) for glob in _CACHE_DIR_GLOBS)


def _find_caches(repo_path: Path) -> list[Path]:
    hits: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        here = Path(dirpath)
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in list(dirnames):
            if _is_cache_dir(name):
                hits.append(here / name)
                dirnames.remove(name)
        hits.extend(here / f for f in filenames if f in _CACHE_FILES)
    return hits


def _scan_orphans(repo_path: Path, directory: Path, tracked: set[str], found: list[Path]) -> None:
    """Record dirs under an orphan root that git tracks no file in. Cache dirs are skipped —
    ``_find_caches`` owns those, so the "orphaned directory" list stays meaningful."""
    rel = directory.relative_to(repo_path).as_posix() + "/"
    if not any(path.startswith(rel) for path in tracked):
        found.append(directory)
        return
    for child in sorted(directory.iterdir()):
        if child.is_dir() and child.name not in _SKIP_DIRS and not _is_cache_dir(child.name):
            _scan_orphans(repo_path, child, tracked, found)


def _find_orphan_dirs(repo_path: Path) -> list[Path]:
    tracked = {line.strip() for line in _git(["ls-files"], repo_path).stdout.splitlines() if line.strip()}
    found: list[Path] = []
    for root in _ORPHAN_ROOTS:
        root_path = repo_path / root
        if root_path.is_dir():
            _scan_orphans(repo_path, root_path, tracked, found)
    return found


def _size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB"):
        if value < 1024:
            return f"{value:.0f}{unit}" if unit == "B" else f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}GB"


def _remove(path: Path) -> int:
    if not path.exists():
        return 0
    size = _size(path)
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)
    return size


def _sweep_trash(repo_path: Path) -> None:
    orphans = _find_orphan_dirs(repo_path)
    caches = [c for c in _find_caches(repo_path) if not any(c == o or o in c.parents for o in orphans)]
    targets = sorted(set(orphans) | set(caches))

    click.echo()
    if not targets:
        success("No local trash to sweep")
        return

    total = sum(_size(path) for path in targets)
    click.echo(f"🧹 Local trash — {len(targets)} paths, ~{_human(total)}:")
    for path in targets:
        click.echo(f"   {path.relative_to(repo_path).as_posix()}")

    if not click.confirm("Remove these?", default=True):
        click.echo("Trash sweep skipped.")
        return

    reclaimed = sum(_remove(path) for path in targets)
    success(f"Removed {len(targets)} paths — reclaimed ~{_human(reclaimed)}")


@click.command()
def main() -> None:
    """Clean up a merged feature branch, then sweep local build/cache trash."""
    repo_path = get_repo_local()
    _branch_cleanup(repo_path)
    _sweep_trash(repo_path)
    click.echo()
    click.echo("🎉 Cleanup complete!")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
