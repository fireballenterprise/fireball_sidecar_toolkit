from invoke import task

from ..tests import actionlint, pylint, pytest, rufflint, yamllint
from . import ruff


@task
def fix(context):
    """Run All Automated Fixes"""
    ruff.fix(context)
    ruff.format(context)


@task
def test(context):
    """Run All Tests"""
    actionlint(context)
    pylint(context)
    pytest(context)
    rufflint(context)
    yamllint(context)
