"""Git/PR workflow tasks — wraps `modules/repo/*.py`. Newly wired here (2026-08-11); the modules
already existed but had no `invoke` task exposing them. `context.run("python -m ...")`, not a
direct import, matching every other task in this repo — this repo's own `tasks/__init__.py`
never adds the repo root to `sys.path`, so a direct `from modules.repo import ...` import would
fail; subprocess-invoking the module lets Python's own `-m` resolve it against the CWD instead.
"""

from invoke import task


@task
def pull(context):
    """Pull updates from git remote (stash → pull --rebase → restore)"""
    context.run("python -m modules.toolkit.repo.pull")


@task
def push(context, no_confirm=False):
    """Push to git remote and iCloud Obsidian folder (fix → test → commit → push)"""
    flag = " --no-confirm" if no_confirm else ""
    context.run(f"python -m modules.toolkit.repo.push{flag}")


@task
def pr_push(context, confirm=True):
    """Push the current feature branch (--confirm/--no-confirm, default: confirm)"""
    flag = "--confirm" if confirm else "--no-confirm"
    context.run(f"python -m modules.toolkit.repo.pr_push {flag}")


@task
def rebase(context):
    """Rebase onto remote default branch (optionally squash first)"""
    context.run("python -m modules.toolkit.repo.rebase")


@task
def squash(context):
    """Anchored squash of all commits to root with optional force push"""
    context.run("python -m modules.toolkit.repo.squash")


@task
def pr_diff(context):
    """Show current branch's commit log/diff vs. its detected base branch"""
    context.run("python -m modules.toolkit.repo.pr_diff")


@task
def pr_notes_save(context, content=None):
    """Save PR notes to tmp/pull_requests/ (--content=...)"""
    flag = f' --content="{content}"' if content else ""
    context.run(f"python -m modules.toolkit.repo.pr_notes{flag}")


@task
def pr_create(context, title=None, content=None):
    """Open a GitHub PR for the current branch (gh pr create)"""
    flags = ""
    if title:
        flags += f' --title="{title}"'
    if content:
        flags += f' --content="{content}"'
    context.run(f"python -m modules.toolkit.repo.pr_create{flags}")


@task
def pr_cleanup(context):
    """Switch to the default branch, pull, and delete the merged local feature branch"""
    context.run("python -m modules.toolkit.repo.pr_cleanup")
