from invoke import task


@task
def pylint(context):
    """Run PyLint on Entire Repo"""
    print("\n------------")
    print("Pylint Lint")
    print("------------\n")
    context.run("pylint --verbose --rcfile=pyproject.toml .")
