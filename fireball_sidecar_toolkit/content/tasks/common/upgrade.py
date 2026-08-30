"""Upgrade tasks for Python and dependencies."""

from invoke import task


@task(default=True)
def upgrade(context):
    """Upgrade Python and Dependencies"""
    print("\n" + "=" * 50)
    print("Upgrade Python and Dependencies")
    print("=" * 50 + "\n")
    context.run("python -m modules.toolkit.versioning.upgrade")


@task
def python(context):
    """Upgrade Python Only"""
    print("\n" + "=" * 50)
    print("Upgrade Python Only")
    print("=" * 50 + "\n")
    context.run("python -m modules.toolkit.versioning.upgrade --python-only")


@task
def libs(context):
    """Upgrade Libraries Only"""
    print("\n" + "=" * 50)
    print("Upgrade Libraries Only")
    print("=" * 50 + "\n")
    context.run("python -m modules.toolkit.versioning.upgrade --libs-only")


@task
def sync(context):
    """Sync Dependencies (no version check)"""
    print("\n" + "=" * 50)
    print("Sync Dependencies")
    print("=" * 50 + "\n")
    context.run("uv sync --upgrade")
