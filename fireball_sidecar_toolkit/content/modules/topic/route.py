"""Route /topic arguments to topic modules."""

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


def _build_flags(args: list[str], *flag_names: str) -> list[str]:
    """Return flags present in args from the allowed set."""
    return [f for f in flag_names if f in args]


def main() -> int:  # noqa: PLR0911
    raw_args = sys.argv[1] if len(sys.argv) > 1 else ""
    args = shlex.split(raw_args)

    if not args:
        return _run("modules.toolkit.topic.list", [])

    first = args[0]

    if first == "new":
        if len(args) < 2:
            sys.stderr.write("Missing path for new topic\n")
            return 1
        flags = [f"--path={args[1]}"]
        if len(args) > 2:
            flags.append(f"--description={' '.join(args[2:])}")
        return _run("modules.toolkit.topic.new", flags)

    if first in ("list", "--list"):
        flags = ["--all"] if any(a in ("all", "--all") for a in args[1:]) else []
        return _run("modules.toolkit.topic.list", flags)

    if first in ("update", "--update"):
        return _run("modules.toolkit.topic.update", _build_flags(args, "--dry-run", "--current-only"))

    if first == "update_list":
        if len(args) < 2:
            sys.stderr.write("Missing path for update_list\n")
            return 1
        return _run("modules.toolkit.topic.update_list", [f"--path={args[1]}"])

    if first == "init":
        flags = [f"--description={' '.join(args[1:])}"] if len(args) > 1 else []
        return _run("modules.toolkit.topic.init", flags)

    # /topic switch <path> or /topic <path> — both switch only (never create)
    switch_path = args[1] if first == "switch" and len(args) > 1 else first if first != "switch" else None
    if switch_path is None:
        sys.stderr.write("Missing path for switch\n")
        return 1
    return _run("modules.toolkit.topic.switch", [f"--path={switch_path}"])


if __name__ == "__main__":
    raise SystemExit(main())
