"""Clean up after a merged PR: switch to the default branch, pull, delete the merged feature branch."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.utils import error, success
from ..setup.properties import get_repo_local
from . import pull as pull_module
from .pr_diff import PROTECTED_BRANCHES, current_branch, detect_base_branch


def _pr_state(repo_path: Path, branch: str) -> str | None:
    """Return the GitHub PR state for `branch` (MERGED, OPEN, CLOSED), or None if no PR is found."""
    result = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "state", "-q", ".state"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip()


@click.command()
def main() -> None:
    """
    Clean up the local feature branch after its PR has been merged on GitHub.

    Steps:
    1. Confirm the current branch has a merged GitHub PR
    2. Switch to the detected default branch (development/main/etc.)
    3. Pull latest changes
    4. Delete the merged local feature branch
    """
    repo_path = get_repo_local()
    branch = current_branch(repo_path)

    if branch in PROTECTED_BRANCHES:
        error(f"Already on protected branch '{branch}' — nothing to clean up.")

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    if status.stdout.strip():
        error("Uncommitted changes on this branch — commit, stash, or discard them first.")

    click.echo(f"🔍 Checking PR status for '{branch}'...")
    state = _pr_state(repo_path, branch)
    if state != "MERGED":
        found = "no PR found" if state is None else f"PR state is {state}"
        error(f"'{branch}' isn't merged yet ({found}). Merge the PR on GitHub first, then re-run.")
    success("PR is merged")
    click.echo()

    base_ref = detect_base_branch(repo_path, branch)
    base_name = base_ref.removeprefix("origin/")

    click.echo(f"🔀 Switching to '{base_name}'...")
    subprocess.run(["git", "checkout", base_name], cwd=repo_path, check=True)
    success(f"Switched to '{base_name}'")
    click.echo()

    click.echo(f"📥 Pulling latest '{base_name}'...")
    pull_module.main()
    click.echo()

    click.echo(f"🗑️  Deleting local branch '{branch}'...")
    subprocess.run(["git", "branch", "-D", branch], cwd=repo_path, check=True)
    success(f"Deleted '{branch}'")

    click.echo()
    click.echo("🎉 Cleanup complete!")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
