"""Invoke wrappers over ``fireball_sidecar_toolkit``. Logic lives in the module; these stay thin."""

from pathlib import Path

from invoke import task

from fireball_sidecar_toolkit import download as _download
from fireball_sidecar_toolkit import release as _release
from fireball_sidecar_toolkit import sync as _sync
from fireball_sidecar_toolkit import upload as _upload
from fireball_sidecar_toolkit.check import check as _check


@task
def check(context):  # noqa: ARG001
    """Read-only drift gate — fail if any generated provider file is stale."""
    _check(Path.cwd())


@task
def download(context):  # noqa: ARG001
    """Clobber _shared/ from the installed fireball-sidecar-toolkit package, then regenerate every provider view."""
    _download.download(Path.cwd())


@task
def release(context):  # noqa: ARG001
    """Promote development -> main and cut a tagged release of the toolkit itself."""
    print(_release.release(Path.cwd()))


@task
def sync(context):  # noqa: ARG001
    """Check _shared/ for local edits, offer to upload them, then download + regenerate."""
    plan = _sync.inspect(Path.cwd())
    print(plan.message)


@task
def upload(context):  # noqa: ARG001
    """Open a PR against fireball_sidecar_toolkit with this repo's _shared/ changes."""
    print(_upload.upload(Path.cwd()))
