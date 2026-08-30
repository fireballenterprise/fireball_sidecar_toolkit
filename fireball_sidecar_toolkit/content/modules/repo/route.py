"""Route /repo arguments to repo modules."""

from __future__ import annotations

import shlex
import subprocess
import sys

from ..common.route_utils import build_env, find_repo_root


def _run(module: str, args: list[str]) -> int:
    repo_root = find_repo_root()
    env = build_env(repo_root)
    cmd = [sys.executable, "-m", module, *args]
    completed = subprocess.run(cmd, cwd=repo_root, env=env, check=False)
    return completed.returncode


_SUBCOMMAND_MODULES = {
    "push": "modules.toolkit.repo.push",
    "pull": "modules.toolkit.repo.pull",
    "pr_diff": "modules.toolkit.repo.pr_diff",
    "pr_notes": "modules.toolkit.repo.pr_notes",
    "pr_create": "modules.toolkit.repo.pr_create",
    "pr_push": "modules.toolkit.repo.pr_push",
    "pr_cleanup": "modules.toolkit.repo.pr_cleanup",
    "rebase": "modules.toolkit.repo.rebase",
    "squash": "modules.toolkit.repo.squash",
}


def main() -> int:
    raw_args = sys.argv[1] if len(sys.argv) > 1 else ""
    args = shlex.split(raw_args)

    if not args:
        sys.stderr.write("Missing repo subcommand\n")
        return 1

    first = args[0]
    module = _SUBCOMMAND_MODULES.get(first)
    if module is None:
        sys.stderr.write(f"Unknown repo subcommand: {first}\n")
        return 1

    return _run(module, args[1:])


if __name__ == "__main__":
    raise SystemExit(main())
