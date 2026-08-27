"""CI/local debugging tasks."""

from invoke import task


@task
def env(context):
    """Print working directory and sorted environment variables for debugging."""
    context.run("pwd && env | sort")
