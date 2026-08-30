"""Repo bootstrap tasks — called by setup.sh, safe to re-run any time."""

from invoke import task


@task
def properties(context):
    """Create/stamp properties.yml with this machine's repo path and git remote"""
    context.run("python -m modules.setup.properties")
