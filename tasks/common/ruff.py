# pylint: disable=W0622 # redefined-builtin

from invoke import task


@task()
def fix(context):
    """Run Ruff Linter on Entire Repo and Fix Safe Offenses"""
    print("\n------------")
    print("Ruff Lint/Fix")
    print("------------\n")
    context.run("ruff check . --fix")


@task()
def format(context):  # noqa: A001
    """Run Ruff Format on Entire Repo and fix"""
    print("\n------------")
    print("Ruff Format")
    print("------------\n")
    context.run("ruff format .")
