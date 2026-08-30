"""Route /chat arguments to chat modules."""

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


def main() -> int:
    raw_args = sys.argv[1] if len(sys.argv) > 1 else ""
    args = shlex.split(raw_args)

    if not args:
        return _run("modules.toolkit.chat.list", [])

    first = args[0]

    if first == "start":
        if len(args) > 1:
            title = " ".join(args[1:])
            return _run("modules.toolkit.chat.start", [f"--title={title}"])
        return _run("modules.toolkit.chat.start", [])

    if first == "end":
        if len(args) > 1:
            message = " ".join(args[1:])
            return _run("modules.toolkit.chat.end", [f"--message={message}"])
        return _run("modules.toolkit.chat.end", [])

    if first == "list":
        sort = args[1] if len(args) > 1 else None
        if sort in ("newest_first", "oldest_first", "alphabetical"):
            return _run("modules.toolkit.chat.list", [f"--sort={sort}"])
        return _run("modules.toolkit.chat.list", [])

    if first == "resume":
        if len(args) > 1:
            pattern = " ".join(args[1:])
            return _run("modules.toolkit.chat.resume", [f"--pattern={pattern}"])
        return _run("modules.toolkit.chat.resume", [])

    return _run("modules.toolkit.chat.list", [])


if __name__ == "__main__":
    raise SystemExit(main())
