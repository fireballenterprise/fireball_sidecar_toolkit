"""Repo VERSION-file bumps. Ported from template_ai_python's `ver` collection (project bits only).

The dependency/action/python version-*check* tasks (`ver.libs` / `ver.python` / `ver.workflows`)
are not carried here yet — they need `tomlkit` + network calls. Add them if `invoke update`
becomes useful for the toolkit itself.
"""

from invoke import task

from modules.versioning import project as project_module


@task
def project_bump_build(_context):
    """Advance VERSION for a dev build (new minor's first build, or next build number)"""
    project_module.bump_build()


@task
def project_bump_release(_context):
    """Finalize VERSION for release by dropping the build suffix"""
    project_module.bump_release()
