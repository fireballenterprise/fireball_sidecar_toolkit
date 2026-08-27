"""``sidecar-toolkit`` console entrypoint.

Thin argparse shell over the primitives so the toolkit works with **no dependency added** via
``uvx --from git+https://github.com/fireballenterprise/fireball_sidecar_toolkit sidecar-toolkit <cmd>`` (e.g. the day-job repo).
The ``invoke sidecar.toolkit.*`` tasks in :mod:`tasks.sidecar.toolkit` are the in-repo equivalents.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import download as _download
from . import sync as _sync
from . import upload as _upload
from .check import check as _check


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sidecar-toolkit", description="Shared AI-agent tooling sync.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Consuming repo root (default: cwd)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="check _shared/ -> offer upload -> download -> render")
    p_sync.add_argument("--yes", action="store_true", help="non-interactive: discard _shared/ edits")

    sub.add_parser("download", help="clobber _shared/ from the package, then render")
    sub.add_parser("upload", help="open a PR against fireball_sidecar_toolkit with local _shared/ changes")
    sub.add_parser("check", help="read-only drift gate")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo: Path = args.repo.resolve()

    if args.command == "download":
        _download.download(repo)
    elif args.command == "upload":
        print(_upload.upload(repo))
    elif args.command == "check":
        _check(repo)
    elif args.command == "sync":
        plan = _sync.inspect(repo)
        print(plan.message)
        if plan.dirty and not args.yes:
            return 2
        _download.download(repo, force=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
