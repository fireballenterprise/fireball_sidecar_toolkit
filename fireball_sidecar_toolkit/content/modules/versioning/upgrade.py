"""Execute Python and/or library upgrades."""

import shutil
import subprocess
from pathlib import Path

from ..common import cli
from ..common.properties import get_repo_local
from ..common.utils import error, info, success, warning

# Import check functions
from .libs import find_updates, get_installed_packages, get_outdated_packages, load_pyproject
from .python import get_current_python_version, get_latest_stable_python


def rebuild_venv(repo_path: Path) -> None:
    """Rebuild virtual environment by removing .venv and running setup.sh."""
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


def check_python_needs_upgrade(repo_path: Path) -> tuple[bool, str, str]:
    """Check if Python needs upgrading.

    Returns:
        (needs_upgrade, current_version, latest_version)
    """
    current_major, current_minor = get_current_python_version(repo_path)
    latest_major, latest_minor, latest_patch = get_latest_stable_python()

    needs_upgrade = current_minor < latest_minor
    current_version = f"{current_major}.{current_minor}"
    latest_version = f"{latest_major}.{latest_minor}.{latest_patch}"

    return (needs_upgrade, current_version, latest_version)


def check_libs_need_upgrade(repo_path: Path) -> tuple[bool, int]:
    """Check if libraries need upgrading.

    Returns:
        (needs_upgrade, count_of_updates)
    """
    installed_packages = get_installed_packages()
    outdated_packages = get_outdated_packages()
    toml_doc, _ = load_pyproject(repo_path)
    lib_updates = find_updates(toml_doc, outdated_packages, installed_packages)

    return (len(lib_updates) > 0, len(lib_updates))


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
        rebuild_venv(repo_path)

    # Libraries upgrade (or just sync if Python was upgraded)
    if upgrade_libs or upgrade_python:
        cli.echo("\n📦 Syncing dependencies...")
        run_uv_sync()

    # === Final Message ===
    cli.echo("\n" + "=" * 60)
    success("Upgrade complete!")

    if upgrade_python:
        cli.echo(f"\n✅ Python upgraded to {python_latest}")
        cli.echo("✅ Virtual environment rebuilt")

    if upgrade_libs:
        cli.echo(f"\n✅ {libs_count} libraries updated")

    cli.echo("\n💡 Changes installed and ready to use")
    cli.echo()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
