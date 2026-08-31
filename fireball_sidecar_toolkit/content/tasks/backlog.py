"""GitHub-Issues backlog tasks — track bugs / features / tasks per family repo (see
`modules/toolkit/backlog/`). `context.run("python -m ...")`, matching every other task here."""

from invoke import task


@task(help={"repo": "target family repo (fuzzy name)", "type": "bug | feature | task", "title": "issue title"})
def add(context, repo=None, type=None, title=None, body="", images="", label="", web=False):  # noqa: A002
    """Open a GitHub Issue on a family repo (native Type + label)"""
    flags = f' --repo "{repo}" --type "{type}" --title "{title}"'
    for name, value in (("body", body), ("images", images), ("label", label)):
        if value:
            flags += f' --{name} "{value}"'
    if web:
        flags += " --web"
    context.run(f"python -m modules.toolkit.backlog.add{flags}")


@task
def close(context, repo=None, number=None, pr="", sha="", reason="completed", comment=""):
    """Close an issue, optionally noting the PR / sha that fixed it"""
    flags = f' --repo "{repo}" --number {number} --reason "{reason}"'
    for name, value in (("pr", pr), ("sha", sha), ("comment", comment)):
        if value:
            flags += f' --{name} "{value}"'
    context.run(f"python -m modules.toolkit.backlog.close{flags}")


@task
def comment(context, repo=None, number=None, body=None, images=""):
    """Add a comment to an issue"""
    flags = f' --repo "{repo}" --number {number} --body "{body}"'
    if images:
        flags += f' --images "{images}"'
    context.run(f"python -m modules.toolkit.backlog.comment{flags}")


@task(name="list")
def list_issues(context, repo="", type="", state="open", limit=30, mine=False, json=False):  # noqa: A002
    """List a repo's issues (defaults to this repo)"""
    flags = f' --state "{state}" --limit {limit}'
    if repo:
        flags += f' --repo "{repo}"'
    if type:
        flags += f' --type "{type}"'
    if mine:
        flags += " --mine"
    if json:
        flags += " --json"
    context.run(f"python -m modules.toolkit.backlog.list{flags}")


@task
def start(context, repo=None, number=None, comment=""):
    """Show + self-assign an issue and print the repo's ship rules"""
    flags = f' --repo "{repo}" --number {number}'
    if comment:
        flags += f' --comment "{comment}"'
    context.run(f"python -m modules.toolkit.backlog.start{flags}")


@task
def view(context, repo=None, number=None, json=False):  # noqa: A002
    """Show one issue"""
    flags = f' --repo "{repo}" --number {number}'
    if json:
        flags += " --json"
    context.run(f"python -m modules.toolkit.backlog.view{flags}")
