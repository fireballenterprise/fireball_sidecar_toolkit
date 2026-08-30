from invoke import task


@task
def actionlint(context):
    """Run Action Lint"""
    print("\n------------")
    print("Action Lint")
    print("------------\n")
    context.run("actionlint")
