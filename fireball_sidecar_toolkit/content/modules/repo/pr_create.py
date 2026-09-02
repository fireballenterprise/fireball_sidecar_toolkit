"""Open a GitHub Pull Request for the current branch via gh."""

from __future__ import annotations

import subprocess

from ..common import cli as click
from ..common.utils import error, success
from ..setup.properties import find_current_repo, get_repo_local
from .pr_diff import current_branch, detect_base_branch


@click.command()
@click.option("--title", default=None, help="Pull request title")
@click.option("--content", default=None, help="Pull request body (markdown)")
def main(title: str | None = None, content: str | None = None) -> None:
    """Open a GitHub PR for the current branch against its detected base branch."""
    self_repo = find_current_repo()
    if self_repo is not None and not self_repo.pull_request:
        error(
            f"{self_repo.name} ships by direct push (pull_request: false in properties.yml) — "
            "not opening a PR. Fast-forward the default branch to your work and push instead."
        )
    if not title or not title.strip():
        error("PR title cannot be empty")
    if not content or not content.strip():
        error("PR notes content cannot be empty")

    repo_path = get_repo_local()
    branch = current_branch(repo_path)
    base_ref = detect_base_branch(repo_path, branch)
    base_name = base_ref.removeprefix("origin/")

    click.echo(f"Creating PR: {branch} -> {base_name}")
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            base_name,
            "--head",
            branch,
            "--title",
            title,
            "--body",
            content,
            "--assignee",
            "@me",
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        if "already exists" in result.stderr.lower():
            existing = subprocess.run(
                ["gh", "pr", "view", "--json", "url", "-q", ".url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if existing.returncode == 0 and existing.stdout.strip():
                success(f"PR already exists: {existing.stdout.strip()}")
                return
        error(f"gh pr create failed:\n{result.stderr}")

    success("PR created!")
    click.echo(result.stdout.strip())


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
