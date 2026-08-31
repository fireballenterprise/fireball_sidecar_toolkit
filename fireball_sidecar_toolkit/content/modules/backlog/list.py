"""`backlog.list` — list a repo's issues (defaults to the current repo).

uv run --no-sync python -m modules.toolkit.backlog.list [--repo vscode] [--type bug] [--label backlog]
"""

from __future__ import annotations

from ..common import cli
from ..common.utils import error
from .common import ISSUE_TYPES, gh, nwo, resolve_repo_or_current


@cli.command()
@cli.option("--repo", default="", help="Family repo (fuzzy name; default: this repo)")
@cli.option("--type", "issue_type", default="", help="Filter by native issue Type: bug | feature | task")
@cli.option("--label", "label_filter", default="", help="Filter by label (area or nature)")
@cli.option("--state", default="open", type=cli.Choice(["open", "closed", "all"]), help="Issue state")
@cli.option("--limit", default=30, type=int, help="Max issues to show")
@cli.option("--mine", is_flag=True, help="Only issues assigned to you")
@cli.option("--json", "as_json", is_flag=True, help="Emit the raw gh JSON array (for scripting)")
def main(
    repo: str = "",
    issue_type: str = "",
    label_filter: str = "",
    state: str = "open",
    limit: int = 30,
    mine: bool = False,
    as_json: bool = False,
) -> None:
    """Print the issue list as gh's table, or the raw JSON with --json."""
    if issue_type and issue_type not in ISSUE_TYPES:
        error(f"--type must be one of {', '.join(ISSUE_TYPES)} (got {issue_type!r})")
    repo_nwo = nwo(resolve_repo_or_current(repo))
    args = ["issue", "list", "--state", state, "--limit", str(limit)]
    if issue_type:
        args += ["--search", f"type:{ISSUE_TYPES[issue_type]}"]
    if label_filter:
        args += ["--label", label_filter]
    if mine:
        args += ["--assignee", "@me"]
    if as_json:
        args += ["--json", "number,title,state,labels,url,createdAt,updatedAt"]
    cli.echo(gh(args, repo=repo_nwo).stdout.rstrip())


if __name__ == "__main__":
    main()
