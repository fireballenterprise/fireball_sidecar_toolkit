"""Invoke tasks shipped *inside the wheel* so a consuming repo mounts them in one line::

    from fireball_sidecar_toolkit.tasks import collection as toolkit_tasks
    namespace.add_collection(toolkit_tasks, name="toolkit")

Every task operates on the repo it is run from (``Path.cwd()``). Logic lives in the sibling
modules; these wrappers stay thin.
"""

from __future__ import annotations

from pathlib import Path

from invoke import Collection, task

from . import sync as _sync
from . import upload as _upload
from .check import check as _check
from .download import download as _download
from .mdfix import check_tree as _md_check
from .mdfix import fix_tree as _md_fix
from .release import release as _release


@task
def download(context):  # noqa: ARG001
    """Clobber .ai/shared/ from the installed toolkit, then regenerate every provider view."""
    result = _download(Path.cwd())
    print(f"Rendered {result.by_count} files.")


@task
def check(context):  # noqa: ARG001
    """Read-only drift gate — fail if any generated provider file (or .ai/shared/) is stale."""
    _check(Path.cwd())
    print("No drift.")


@task
def mdfix(context, check=False):  # noqa: ARG001
    """Normalise every *.md (no blank line after a header; no stray --- divider in instructions).

    Pass --check for the read-only gate (raises instead of writing) — wired into `invoke test`.
    """
    if check:
        _md_check(Path.cwd())
        print("Markdown OK.")
        return
    changed = _md_fix(Path.cwd(), write=True)
    print(f"Normalised {len(changed)} markdown file(s).")


@task
def sync(context, force=False):  # noqa: ARG001
    """Inspect .ai/shared/ for local edits; if clean (or force), clobber + regenerate."""
    plan = _sync.inspect(Path.cwd())
    print(plan.message)
    if plan.dirty and not force:
        raise SystemExit(2)
    result = _sync.run(Path.cwd(), force=True)
    print(f"Rendered {result.by_count} files.")


@task
def upload(context, branch=None, toolkit_repo=None):  # noqa: ARG001
    """Open a PR against fireball_sidecar_toolkit with this repo's .ai/shared/ edits.

    The toolkit checkout is found via --toolkit-repo, then $FIREBALL_SIDECAR_TOOLKIT_REPO,
    then a sibling ../fireball_sidecar_toolkit dir.
    """
    kwargs = {"branch": branch}
    if toolkit_repo:
        kwargs["toolkit_repo"] = Path(toolkit_repo)
    print(_upload.upload(Path.cwd(), **kwargs))


@task
def release(context):  # noqa: ARG001
    """Dispatch the toolkit's development -> main release workflow."""
    print(_release(Path.cwd()))


collection = Collection("toolkit")
for _task in (download, check, mdfix, sync, upload, release):
    collection.add_task(_task)
