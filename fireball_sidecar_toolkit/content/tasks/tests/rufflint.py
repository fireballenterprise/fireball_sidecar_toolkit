from invoke import task


@task
def rufflint(context):
    """Run Ruff Linter on Entire Repo"""
    print("\n------------")
    print("Ruff Lint")
    print("------------\n")
    context.run("ruff check .")
