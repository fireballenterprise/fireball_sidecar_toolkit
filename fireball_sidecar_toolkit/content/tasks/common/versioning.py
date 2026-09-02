"""Version-lock check tasks — compare pyproject.toml deps and workflow actions against latest releases."""

from invoke import task

# libs exits 3 when everything is already up to date
_OK_EXIT_CODES = (0, 3)


def _run_module(context, module, dry_run, yes):
    flags = ""
    if dry_run:
        flags += " --dry-run"
    if yes:
        flags += " --yes"
    result = context.run(f"python -m {module}{flags}", warn=True)
    if result.exited not in _OK_EXIT_CODES:
        raise SystemExit(result.exited)


@task
def libs(context, dry_run=False, yes=False):
    """Check pyproject.toml dependencies against latest releases and update version locks"""
    _run_module(context, "modules.toolkit.versioning.libs", dry_run, yes)


@task
def project_bump_patch(context):
    """X.Y.Z -> X.Y.(Z+1). Every merge to development."""
    context.run("python -m modules.toolkit.versioning.project patch")


@task
def project_bump_minor(context):
    """X.Y.Z -> X.(Y+1).0. A milestone release bump (release workflow bump=minor)."""
    context.run("python -m modules.toolkit.versioning.project minor")


@task
def project_bump_major(context):
    """X.Y.Z -> (X+1).0.0. A major release bump (release workflow bump=major)."""
    context.run("python -m modules.toolkit.versioning.project major")


@task
def project_bump_build(context):
    """X.Y.Z -> X.Y.Z-001 -> -002. Manual feature-branch use only; never merged or published."""
    context.run("python -m modules.toolkit.versioning.project build")


@task
def python(context, dry_run=False, yes=False):
    """Check the pinned Python version against the latest release and update config references"""
    _run_module(context, "modules.toolkit.versioning.python", dry_run, yes)


@task
def workflows(context, dry_run=False, yes=False):
    """Check .github/workflows/ action refs against latest major versions and update them"""
    _run_module(context, "modules.toolkit.versioning.workflows", dry_run, yes)


@task
def update(context, dry_run=False, yes=False):
    """Backfill properties.yml from the tier fragments, then run every version check (libs, python,
    workflows) — each runs even if an earlier one exits early."""
    context.run("python -m modules.toolkit.setup.properties")
    for check in (libs, python, workflows):
        try:
            check(context, dry_run=dry_run, yes=yes)
        except SystemExit:  # noqa: PERF203
            pass
