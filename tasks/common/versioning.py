"""Repo VERSION-file bumps. VERSION (PEP 440 X.Y.Z) is the single source of truth — pyproject
reads it via `[tool.setuptools.dynamic]`.

The dependency/action/python version-*check* tasks (`ver.libs` / `ver.python` / `ver.workflows`)
from template_ai_python are not carried here yet — they need `tomlkit` + network calls.
"""

from invoke import task

from modules.versioning import project as project_module


@task
def project_bump_patch(_context):
    """X.Y.Z -> X.Y.(Z+1). Every PR merge to development."""
    project_module.bump_patch()


@task
def project_bump_minor(_context):
    """X.Y.Z -> X.(Y+1).0. The default release bump."""
    project_module.bump_minor()


@task
def project_bump_major(_context):
    """X.Y.Z -> (X+1).0.0. Milestone releases (e.g. the official 1.0.0)."""
    project_module.bump_major()


@task
def project_bump_build(_context):
    """X.Y.Z -> X.Y.Z-001 -> -002. Manual feature-branch use only; never published."""
    project_module.bump_build()
