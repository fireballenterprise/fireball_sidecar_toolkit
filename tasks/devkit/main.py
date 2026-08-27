"""Invoke wrappers over ``modules.devkit``. Logic lives in the module; these stay thin."""

from pathlib import Path

from invoke import task

from modules.devkit import download as _download
from modules.devkit import sync as _sync
from modules.devkit import upload as _upload
from modules.devkit.check import check as _check


@task
def check(context):  # noqa: ARG001
    """Read-only drift gate — fail if any generated provider file is stale."""
    _check(Path.cwd())


@task
def download(context):  # noqa: ARG001
    """Clobber _shared/ from the installed ai-devkit package, then regenerate every provider view."""
    _download.download(Path.cwd())


@task
def sync(context):  # noqa: ARG001
    """Check _shared/ for local edits, offer to upload them, then download + regenerate."""
    plan = _sync.inspect(Path.cwd())
    print(plan.message)


@task
def upload(context):  # noqa: ARG001
    """Open a PR against ai_devkit with this repo's _shared/ changes."""
    print(_upload.upload(Path.cwd()))
