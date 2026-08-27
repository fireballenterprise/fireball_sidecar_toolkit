from invoke import task


@task(name="pytest")
def run_pytest(context, scope=None):
    """Run Pytest Unit Test Suite (pass scope=<marker-expr> to run a subset, e.g. scope=setup or scope="not style")"""
    print("\n------------")
    print("Pytest")
    print("------------\n")
    context.run(f'pytest -m "{scope}"' if scope else "pytest")
