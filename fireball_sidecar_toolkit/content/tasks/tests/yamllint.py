from invoke import task


@task
def yamllint(context):
    """Run Yaml Linter on Entire Repo"""
    print("\n------------")
    print("Yaml Lint")
    print("------------\n")
    context.run(
        """
        yamllint --list-files -c .yamllint . &&
        echo '------------' &&
        echo -e &&
        yamllint -f parsable -c .yamllint .
        """
    )
