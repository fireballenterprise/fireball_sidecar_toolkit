"""uv sync tasks — install the dependency versions currently locked in pyproject.toml."""

from invoke import task


@task
def upgrade_bin(context):
    """Upgrading UV Binary (Not Version Locked)"""
    print("\n------------")
    print("brew upgrade uv")
    print("------------\n")
    context.run("brew upgrade uv")


@task
def upgrade_libs(context):
    """Install the dependency versions currently locked in pyproject.toml (uv sync)"""
    print("\n------------")
    print("uv sync")
    print("------------\n")
    context.run("uv sync")
