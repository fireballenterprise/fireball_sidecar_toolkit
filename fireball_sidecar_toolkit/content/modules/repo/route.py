"""Route /repo arguments to repo modules.

``/repo`` with no args prints usage. ``/repo list`` shows the ``repos:`` family map;
``/repo apply`` points at the agent-driven Cross-Repo Change Workflow. ``pull`` / ``push`` /
``cleanup`` act on the current repo, or on the family when a scope token follows — ``all`` (whole
family), ``ai`` (``ai: true``), or ``dev_prd`` (``default_branch: development``); handled by
:mod:`modules.toolkit.repo.family`. Everything else dispatches straight to its module.
"""

from __future__ import annotations

import shlex
import subprocess
import sys

from ..common.route_utils import build_env, find_repo_root
from ..setup.properties import FAMILY_SCOPES
from . import family

_PREFIX = "modules.toolkit.repo"

_SUBCOMMAND_MODULES = {
    "push": f"{_PREFIX}.push",
    "pull": f"{_PREFIX}.pull",
    "cleanup": f"{_PREFIX}.cleanup",
    "pr_cleanup": f"{_PREFIX}.cleanup",  # back-compat alias for the old name
    "pr_diff": f"{_PREFIX}.pr_diff",
    "pr_notes": f"{_PREFIX}.pr_notes",
    "pr_create": f"{_PREFIX}.pr_create",
    "pr_push": f"{_PREFIX}.pr_push",
    "rebase": f"{_PREFIX}.rebase",
    "squash": f"{_PREFIX}.squash",
}

_FAMILY_VERBS = ("pull", "push", "cleanup")
_SCOPE_TOKENS = ("all", *FAMILY_SCOPES)

_USAGE = """\
/repo — repo and repo-family operations

  /repo list                    show the repos: family map (parent tree + attributes)
  /repo self                    this repo's repos: attributes (ship flags, default branch, …)
  /repo pull [all|ai|dev_prd]    git pull (this repo | family scope)
  /repo push [all|ai|dev_prd]    fix + test + commit + push (this repo | family scope)
  /repo cleanup [all|ai|dev_prd] post-merge branch cleanup + local-trash sweep
  /repo apply <description>      port a change across the family (two-phase, agent-driven)

Scopes: all = whole family · ai = ai:true repos · dev_prd = default_branch development.
Aliases: /pull, /push, /cleanup — each also takes a scope. Retired repos are always skipped.
"""

_APPLY_POINTER = """\
Cross-repo apply is agent-driven. Follow the Cross-Repo Change Workflow in
.ai/toolkit/instructions/repos.md: apply the change on a feature branch in every family repo
(root-to-leaf parent order), stop at the checkpoint, then ship each per its pull_request flag
(a PR for pull_request:true, a direct push to the default branch for pull_request:false).
"""


def _run(module: str, args: list[str]) -> int:
    repo_root = find_repo_root()
    completed = subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=repo_root,
        env=build_env(repo_root),
        check=False,
    )
    return completed.returncode


def _usage(*, err: bool = False) -> int:
    (sys.stderr if err else sys.stdout).write(_USAGE)
    return 1 if err else 0


def main() -> int:
    args = shlex.split(sys.argv[1] if len(sys.argv) > 1 else "")

    if not args or args[0] in ("help", "-h", "--help"):
        return _usage()

    first, rest = args[0], args[1:]

    if first == "list":
        return family.print_map()

    if first == "self":
        return family.print_self()

    if first == "apply":
        sys.stdout.write(_APPLY_POINTER)
        return 0

    if first in _FAMILY_VERBS:
        scopes = [token for token in rest if token in _SCOPE_TOKENS]
        if scopes:
            scope = None if scopes[0] == "all" else scopes[0]
            return family.run_family(first, assume_yes="--yes" in rest or "-y" in rest, scope=scope)

    module = _SUBCOMMAND_MODULES.get(first)
    if module is None:
        sys.stderr.write(f"Unknown repo subcommand: {first!r}\n\n")
        return _usage(err=True)

    return _run(module, rest)


if __name__ == "__main__":
    raise SystemExit(main())
