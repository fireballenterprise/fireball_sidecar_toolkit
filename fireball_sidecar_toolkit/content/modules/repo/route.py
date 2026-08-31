"""Route /repo arguments to repo modules.

``/repo`` with no args prints usage. ``/repo list`` shows the ``repos:`` family map;
``/repo apply`` points at the agent-driven Cross-Repo Change Workflow. ``pull`` / ``push`` /
``cleanup`` act on the current repo, or on the whole family when the ``all`` token is present
(handled by :mod:`modules.toolkit.repo.family`). Everything else dispatches straight to its module.
"""

from __future__ import annotations

import shlex
import subprocess
import sys

from ..common.route_utils import build_env, find_repo_root
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

_USAGE = """\
/repo — repo and repo-family operations

  /repo list                show the repos: / lineage: family map
  /repo pull [all]          git pull (this repo | whole family)
  /repo push [all]          fix + test + commit + push (this repo | whole family)
  /repo cleanup [all]       post-merge branch cleanup + local-trash sweep
  /repo apply <description>  port a change across the family (two-phase, agent-driven)

Aliases: /pull, /push, /cleanup — each also takes `all`.
"""

_APPLY_POINTER = """\
Cross-repo apply is agent-driven. Follow the Cross-Repo Change Workflow in
.ai/toolkit/instructions/repos.md: apply the change on a feature branch in every family repo
(root-to-leaf lineage order), stop at the checkpoint, then ship one PR per repo.
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

    if first == "apply":
        sys.stdout.write(_APPLY_POINTER)
        return 0

    if first in _FAMILY_VERBS and "all" in rest:
        return family.run_family(first, assume_yes="--yes" in rest or "-y" in rest)

    module = _SUBCOMMAND_MODULES.get(first)
    if module is None:
        sys.stderr.write(f"Unknown repo subcommand: {first!r}\n\n")
        return _usage(err=True)

    return _run(module, rest)


if __name__ == "__main__":
    raise SystemExit(main())
