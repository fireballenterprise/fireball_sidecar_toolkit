"""Fan a ``/repo`` verb across the whole ``repos:`` family (pull / push / cleanup).

``/repo <verb>`` acts on the current repo; ``/repo <verb> all`` routes here and runs the verb
against every repo in ``properties.yml``'s ``repos:`` map, in root-to-leaf ``lineage:`` order.
``pull`` is done inline (switch to the verified default branch + ``--ff-only``); ``push`` and
``cleanup`` shell out to each repo's own vendored module so the target's real ``invoke test`` /
``gh`` calls run in its own checkout.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ..common import cli
from ..common.route_utils import REPO_ROOT_ENV, build_env
from ..common.utils import expand_path
from ..setup.properties import FamilyRepo, get_family_repos, get_properties, get_repo_local

_SINGLETON_NOTE = (
    "ℹ  'all' requested, but properties.yml has no repos: family map — running just this repo.\n"
    "   Add a repos: key (see .ai/toolkit/instructions/repos.md) to enable family-wide runs."
)


def _pkg_root(path: Path) -> str:
    """Importable prefix for a repo's vendored toolkit modules (consumer vs. template layout)."""
    return "modules.toolkit" if (path / "modules" / "toolkit" / "repo").is_dir() else "modules"


def _repo_module(path: Path, verb: str) -> str:
    """The ``python -m`` target for ``verb`` inside ``path`` (handles the pr_cleanup→cleanup rename
    in family repos that haven't synced the new toolkit yet)."""
    pkg = _pkg_root(path)
    if verb == "cleanup":
        repo_dir = path / pkg.replace(".", "/") / "repo"
        leaf = "cleanup" if (repo_dir / "cleanup.py").exists() else "pr_cleanup"
        return f"{pkg}.repo.{leaf}"
    return f"{pkg}.repo.{verb}"


def _git(args: list[str], path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=path, capture_output=True, text=True, check=False)


def _default_branch(path: Path) -> str:
    """GitHub's default branch for this clone; falls back to origin/HEAD, then ``main``.

    A local clone's ``origin/HEAD`` can go stale (still ``main`` after the remote moved to
    ``development``), so ``gh`` is the primary source and we reset ``origin/HEAD`` to match.
    """
    gh = subprocess.run(
        ["gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
        cwd=path,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = gh.stdout.strip()
    if branch:
        return branch
    head = _git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], path).stdout.strip()
    return head.removeprefix("origin/") or "main"


def _pull_one(repo: FamilyRepo) -> tuple[str, str]:
    """Bring one clone's default branch up to date. Returns ``(status, detail)``."""
    branch = _default_branch(repo.path)
    _git(["remote", "set-head", "origin", branch], repo.path)

    dirty = bool(_git(["status", "--porcelain"], repo.path).stdout.strip())
    if dirty and _git(["stash", "push", "-u", "-m", "repo pull all"], repo.path).returncode != 0:
        return "error", "could not stash a dirty tree"

    if _git(["checkout", branch], repo.path).returncode != 0:
        if dirty:
            _git(["stash", "pop"], repo.path)
        return "error", f"checkout {branch} failed"

    _git(["fetch", "--prune", "origin"], repo.path)
    before = _git(["rev-parse", "HEAD"], repo.path).stdout.strip()
    pull = _git(["pull", "--ff-only", "origin", branch], repo.path)
    after = _git(["rev-parse", "HEAD"], repo.path).stdout.strip()

    note = ""
    if dirty and _git(["stash", "pop"], repo.path).returncode != 0:
        note = " (stash pop conflicted — left in stash)"

    if pull.returncode != 0:
        tail = pull.stderr.strip().splitlines()[-1] if pull.stderr.strip() else "pull failed"
        return "error", tail + note
    if before == after:
        return "current", f"{branch} @ {after[:8]}{note}"
    return "updated", f"{before[:8]} → {after[:8]}{note}"


def _run_module(repo: FamilyRepo, verb: str) -> tuple[str, str]:
    """Run a repo's own ``push`` / ``cleanup`` module in its own checkout + venv.

    ``push`` takes a ``--no-confirm`` flag; ``cleanup`` takes no argv (it calls ``pull``'s command
    entrypoint internally) so its prompt is suppressed with ``AUTO_CONFIRM`` instead.
    """
    module = _repo_module(repo.path, verb)
    env = build_env(repo.path)
    env[REPO_ROOT_ENV] = str(repo.path)
    extra = ["--no-confirm"] if verb == "push" else []
    if verb == "cleanup":
        env["AUTO_CONFIRM"] = "1"
    completed = subprocess.run(
        ["uv", "run", "--no-sync", "python", "-m", module, *extra],
        cwd=repo.path,
        env=env,
        check=False,
    )
    return ("ok", "") if completed.returncode == 0 else ("error", f"exit {completed.returncode}")


def _dispatch_single(verb: str) -> int:
    """Singleton fallback: run the single-repo verb against the current repo."""
    path = get_repo_local()
    completed = subprocess.run(
        [sys.executable, "-m", _repo_module(path, verb)],
        cwd=path,
        env=build_env(path),
        check=False,
    )
    return completed.returncode


_STATUS_MARK = {"updated": "✓", "current": "·", "ok": "✓", "error": "✗"}


def _print_summary(verb: str, results: list[tuple[str, str, str]]) -> None:
    cli.echo(f"\n─── /repo {verb} all — summary ───")
    width = max(len(label) for label, _, _ in results)
    for label, status, detail in results:
        mark = _STATUS_MARK.get(status, " ")
        cli.echo(f"  {mark} {label.ljust(width)}  {status}{f'  {detail}' if detail else ''}")
    failed = [label for label, status, _ in results if status == "error"]
    if failed:
        cli.echo(f"\n{len(failed)} failed: {', '.join(failed)}")


def run_family(verb: str, *, assume_yes: bool = False) -> int:
    """Run ``verb`` (``pull`` | ``push`` | ``cleanup``) across the whole family."""
    repos = get_family_repos(include_self=True)
    if len(repos) <= 1:
        cli.echo(_SINGLETON_NOTE)
        cli.echo()
        return _dispatch_single(verb)

    if verb in ("push", "cleanup") and not assume_yes:
        cli.echo(f"/repo {verb} all — {len(repos)} repos:")
        for repo in repos:
            cli.echo(f"  • {repo.org}/{repo.name}")
        if verb == "push":
            cli.echo("\nEach runs the full /push: invoke fix + invoke test + commit + push.")
        if not cli.confirm(f"Run '{verb}' in all {len(repos)} repos?", default=False):
            cli.echo("Cancelled.")
            return 1

    results: list[tuple[str, str, str]] = []
    for repo in repos:
        label = f"{repo.org}/{repo.name}"
        cli.echo(f"\n═══ {label} ═══")
        status, detail = _pull_one(repo) if verb == "pull" else _run_module(repo, verb)
        results.append((label, status, detail))

    _print_summary(verb, results)
    return 0 if all(status != "error" for _, status, _ in results) else 1


def _lineage_lines(node: object, indent: int) -> list[str]:
    """Render a nested ``lineage:`` value (list of names / single-key dicts) as an indented tree."""
    lines: list[str] = []
    for item in node or []:
        if isinstance(item, dict):
            name, kids = next(iter(item.items()))
            lines.append(" " * indent + str(name))
            lines.extend(_lineage_lines(kids, indent + 2))
        else:
            lines.append(" " * indent + str(item))
    return lines


def print_map() -> int:
    """Print the ``repos:`` / ``lineage:`` family map + which clones exist locally."""
    props = get_properties()
    repos = props.get("repos") or {}
    if not repos or set(repos) <= {"lineage"}:
        cli.echo("No repos: family map in properties.yml — this repo has no related-repo family.")
        return 0

    repos_local = props.get("repos_local") or {}
    self_path = get_repo_local().resolve()

    cli.echo("Repo family (properties.yml → repos:)\n")
    for org, names in repos.items():
        if org == "lineage":
            continue
        base = next((value for key, value in repos_local.items() if key.lower() == org.lower()), None)
        cli.echo(f"{org}/")
        for name in sorted(names):
            path = (expand_path(base) / name).resolve() if base else None
            here = "  ← this repo" if path == self_path else ""
            missing = "" if path and (path / ".git").exists() else "  [no local clone]"
            cli.echo(f"  {name}{here}{missing}")
        cli.echo()

    lineage = repos.get("lineage")
    if lineage:
        cli.echo("lineage (parent → stamped child):")
        for root, kids in lineage.items():
            cli.echo(f"  {root}")
            for line in _lineage_lines(kids, 4):
                cli.echo(line)
    return 0
