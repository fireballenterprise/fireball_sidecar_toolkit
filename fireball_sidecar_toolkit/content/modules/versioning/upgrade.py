"""Execute Python and/or library upgrades."""

import logging
import shutil
import subprocess
from pathlib import Path

from ..common import cli
from ..common.utils import error, info, success, version_tuple, warning
from ..setup.properties import get_binary_version, get_repo_local

# Import check functions
from .libs import get_declared_dependency_names, get_outdated_packages, load_pyproject
from .python import get_runtime_python_version
from .sdkman import read_sdkmanrc

LOGGER = logging.getLogger(__name__)


def rebuild_venv(repo_path: Path, python_version: str) -> None:
    """Install `python_version` via uv, then remove .venv and recreate it (via setup.sh) so the
    rebuilt venv lands on exactly that version rather than whatever setup.sh's own floating
    `--python` spec happens to resolve to."""
    info(f"Installing Python {python_version}...")
    result = subprocess.run(["uv", "python", "install", python_version], check=False)
    if result.returncode != 0:
        error(f"uv python install {python_version} failed")

    venv_path = repo_path / ".venv"

    if venv_path.exists():
        cli.echo("🗑️  Removing existing .venv...")
        shutil.rmtree(venv_path)

    cli.echo("🏗️  Running setup.sh to create new .venv...")
    result = subprocess.run(
        ["bash", "setup.sh"],
        cwd=repo_path,
        check=False,
    )

    if result.returncode != 0:
        warning("setup.sh completed with warnings")
    else:
        success("Virtual environment rebuilt successfully")


def run_uv_sync() -> None:
    """Run uv sync --upgrade to install updated dependencies."""
    info("Syncing dependencies with uv...")

    result = subprocess.run(
        ["uv", "sync", "--upgrade"],
        check=False,
    )

    if result.returncode != 0:
        error("uv sync --upgrade failed")

    success("Dependencies synced")


def check_python_needs_upgrade(_repo_path: Path) -> tuple[bool, str, str]:
    """Check whether the active Python runtime matches properties.yml's pinned version — the
    exact version `/update python` last wrote there, and the one this upgrade installs (kept as
    the single source of truth, same as `binary_versions.cdk`/`aws.cdk.upgrade`).

    Returns:
        (needs_upgrade, current_runtime_version, pinned_version)
    """
    current_runtime = get_runtime_python_version()
    try:
        pinned_version = get_binary_version("python")
    except KeyError:
        return (False, current_runtime, current_runtime)  # no binary_versions.python pin — nothing to do
    needs_upgrade = version_tuple(current_runtime) < version_tuple(pinned_version)

    return (needs_upgrade, current_runtime, pinned_version)


def check_libs_need_upgrade(repo_path: Path) -> tuple[bool, int]:
    """Check if any declared dependency has an installed version older than what's available.

    Compares *installed* package versions against `uv pip list --outdated`, not pyproject.toml's
    specifier string against the latest version (that's `find_updates`, used by `ver.libs` to
    detect config drift) — `/update` may already have bumped the specifier before the matching
    `uv sync --upgrade` ever ran, which would make a specifier-vs-latest check report nothing to
    do even though `.venv`/`uv.lock` are still on the old version.

    Returns:
        (needs_upgrade, count_of_updates)
    """
    outdated_packages = get_outdated_packages()
    toml_doc, _ = load_pyproject(repo_path)
    declared = get_declared_dependency_names(toml_doc)

    relevant_outdated = [pkg for pkg in outdated_packages if pkg["name"].lower() in declared]
    return (len(relevant_outdated) > 0, len(relevant_outdated))


def sdkman_env_install(repo_path: Path) -> None:
    """`sdk env install` in `repo_path` — installs whatever `.sdkmanrc` pins (the pins are set by
    `/update`, i.e. `python -m modules.toolkit.versioning.sdkman`). `sdk` is a shell function, so
    this goes through a login shell that sources sdkman-init.sh."""
    info("Installing .sdkmanrc toolchain via SDKMAN...")
    result = subprocess.run(
        ["bash", "-lc", 'source "$HOME/.sdkman/bin/sdkman-init.sh" && sdk env install'],
        cwd=repo_path,
        check=False,
    )
    if result.returncode != 0:
        warning("sdk env install completed with warnings — check `sdk env` output")
    else:
        success("SDKMAN toolchain installed")


@cli.command()
@cli.option("--yes", "-y", "no_confirm", is_flag=True, help="Skip confirmation")
@cli.option("--python-only", is_flag=True, help="Only upgrade Python")
@cli.option("--libs-only", is_flag=True, help="Only upgrade libraries")
def main(no_confirm: bool, python_only: bool, libs_only: bool) -> None:
    """
    Execute upgrades for Python and/or dependencies.

    This command performs actual installations:
    - Downloads and installs new Python versions
    - Rebuilds .venv if Python changed
    - Runs uv sync --upgrade to install updated dependencies

    IMPORTANT: Run /update first to update config files before upgrading.

    Examples:
        /upgrade                  # Upgrade everything
        /upgrade --python-only    # Only Python
        /upgrade --libs-only      # Only libraries
        /upgrade --yes            # Skip confirmation
    """
    repo_path = get_repo_local()

    # Determine what to upgrade
    upgrade_python = not libs_only
    upgrade_libs = not python_only

    # Check what needs upgrading
    python_needs_upgrade, python_current, python_latest = check_python_needs_upgrade(repo_path)
    libs_need_upgrade, libs_count = check_libs_need_upgrade(repo_path)
    # SDKMAN toolchain — only the full `upgrade` touches it, and only when a `.sdkmanrc` exists.
    # `/update` has already rewritten the pins by now; this just installs them.
    upgrade_sdkman = not python_only and not libs_only and bool(read_sdkmanrc(repo_path))

    # Filter based on flags
    if upgrade_python and not python_needs_upgrade:
        upgrade_python = False
    if upgrade_libs and not libs_need_upgrade:
        upgrade_libs = False

    # === Display Summary ===
    cli.echo("\n" + "=" * 60)
    cli.echo("🚀 UPGRADE SUMMARY")
    cli.echo("=" * 60)

    will_upgrade = []

    if upgrade_python:
        cli.echo(f"\n🐍 Python: {python_current} → {python_latest}")
        cli.echo("   Actions:")
        cli.echo("   - Install new Python version")
        cli.echo("   - Rebuild .venv")
        will_upgrade.append("Python")
    elif python_only:
        cli.echo(f"\n🐍 Python: {python_current} (already up to date)")

    if upgrade_libs:
        cli.echo(f"\n📦 Libraries: {libs_count} updates available")
        cli.echo("   Actions:")
        cli.echo("   - Run uv sync --upgrade")
        will_upgrade.append(f"{libs_count} libraries")
    elif libs_only:
        cli.echo("\n📦 Libraries: Already up to date")

    if upgrade_sdkman:
        cli.echo("\n☕ SDKMAN toolchain: .sdkmanrc present")
        cli.echo("   Actions:")
        cli.echo("   - Run sdk env install (installs whatever .sdkmanrc pins)")
        will_upgrade.append("SDKMAN toolchain")

    if not will_upgrade:
        cli.echo("\n" + "=" * 60)
        success("Everything is already up to date!")
        cli.echo("\n💡 Nothing to upgrade")
        raise SystemExit(0)

    # === Confirmation ===
    if not no_confirm:
        cli.echo("\n" + "=" * 60)
        upgrade_summary = " and ".join(will_upgrade)

        if not cli.confirm(f"💡 Proceed with upgrading {upgrade_summary}?"):
            cli.echo("Cancelled.")
            raise SystemExit(2)

    # === Execute Upgrades ===
    cli.echo("\n" + "=" * 60)
    cli.echo("⚙️  EXECUTING UPGRADES...")
    cli.echo("=" * 60)

    # Python upgrade (includes venv rebuild)
    if upgrade_python:
        cli.echo(f"\n🐍 Upgrading Python to {python_latest}...")
        rebuild_venv(repo_path, python_latest)

    # Libraries upgrade (or just sync if Python was upgraded)
    if upgrade_libs or upgrade_python:
        cli.echo("\n📦 Syncing dependencies...")
        run_uv_sync()

    if upgrade_sdkman:
        cli.echo("\n☕ Installing SDKMAN toolchain...")
        sdkman_env_install(repo_path)

    # === Final Message ===
    cli.echo("\n" + "=" * 60)
    success("Upgrade complete!")

    if upgrade_python:
        cli.echo(f"\n✅ Python upgraded to {python_latest}")
        cli.echo("✅ Virtual environment rebuilt")

    if upgrade_libs:
        cli.echo(f"\n✅ {libs_count} libraries updated")

    if upgrade_sdkman:
        cli.echo("\n✅ SDKMAN toolchain installed (`sdk env` to activate in a shell)")

    cli.echo("\n💡 Changes installed and ready to use")
    cli.echo()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
