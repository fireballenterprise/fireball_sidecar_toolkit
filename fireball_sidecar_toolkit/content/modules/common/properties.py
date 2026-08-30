"""Properties management for AI research repository."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _expand_path(value: str) -> Path:
    """Expand ~ and environment variables (e.g. $HOME) in a properties.yml path value."""
    return Path(os.path.expandvars(os.path.expanduser(value)))


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    """
    Find repository root by searching upward for properties.yml.

    Works from any subdirectory within the repository.

    Returns:
        Path to repository root.

    Raises:
        FileNotFoundError: If properties.yml cannot be found.
    """
    # Start from current file location
    current = Path(__file__).resolve()

    # Search upward from current file location
    for parent in [current.parent.parent.parent] + list(current.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    # Also try from current working directory
    current_cwd = Path.cwd().resolve()
    for parent in [current_cwd] + list(current_cwd.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    msg = "Could not find repository root (properties.yml not found)"
    raise FileNotFoundError(msg)


@lru_cache(maxsize=1)
def get_properties() -> dict[str, Any]:
    """
    Load properties.yml with singleton pattern (cached).

    Returns:
        Dictionary with all repository properties.

    Raises:
        FileNotFoundError: If properties.yml does not exist.
    """
    repo_root = get_repo_root()
    props_file = repo_root / "properties.yml"

    with props_file.open() as f:
        return yaml.safe_load(f)


def get_repo_local() -> Path:
    """
    Get repo local path as Path object.

    Returns:
        Path to local repository.
    """
    props = get_properties()
    return _expand_path(props["repo"]["local"])


def get_repo_remote() -> str:
    """
    Get repo remote URL.

    Returns:
        Remote repository URL.
    """
    props = get_properties()
    return props["repo"]["remote"]


def is_icloud_enabled() -> bool:
    """
    Whether iCloud-Obsidian sync is turned on for /push and /pull.

    Off by default. Missing `icloud` section or `icloud.enabled` → False.

    Returns:
        True when `icloud.enabled` is truthy in properties.yml.
    """
    props = get_properties()
    return bool(props.get("icloud", {}).get("enabled", False))


def get_icloud_path() -> Path:
    """
    Get iCloud sync path as Path object.

    Returns:
        Path to iCloud sync location.
    """
    props = get_properties()
    return _expand_path(props["icloud"]["path"])


def get_screenshots_location() -> Path:
    """
    Get screenshots directory path as Path object.

    Returns:
        Path to screenshots directory.
    """
    props = get_properties()
    return _expand_path(props["screenshots"]["location"])


def get_screenshots_latest_file() -> str:
    """
    Get latest screenshot filename.

    Returns:
        Filename for latest screenshot.
    """
    props = get_properties()
    return props["screenshots"]["latest_file"]


def get_screenshots_preserve_files() -> list[str]:
    """
    Get list of screenshot files to preserve during cleanup.

    Returns:
        List of filenames to preserve.
    """
    props = get_properties()
    return props["screenshots"]["preserve_files"]


def get_screenshots_cleanup_patterns() -> list[str]:
    """
    Get list of file patterns to clean up.

    Returns:
        List of glob patterns for cleanup.
    """
    props = get_properties()
    return props["screenshots"]["cleanup_patterns"]


def get_card_progress_csv() -> Path:
    """
    Get card progress CSV path.

    Returns:
        Path to card progress CSV file.
    """
    props = get_properties()
    repo_local = get_repo_local()
    csv_path = props["financials"]["card_progress_csv"]
    return repo_local / csv_path


def get_resume_work_history_md() -> Path:
    """
    Get path to the employment work history markdown file (raw resume source material).

    Returns:
        Path to work_history.md.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["work_history_md"]


def get_resume_guidelines_md() -> Path:
    """
    Get path to the resume guidelines markdown file (filtering/positioning strategy).

    Returns:
        Path to resume_guidelines.md.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["guidelines_md"]


def get_resume_raw_dir() -> Path:
    """
    Get the directory where in-progress raw resume drafts (JSON) are written.

    Returns:
        Path to the resume raw/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["raw_dir"]


def get_resume_templates_dir() -> Path:
    """
    Get the directory holding reusable resume starting templates (JSON).

    Returns:
        Path to the resume templates/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["templates_dir"]


def get_resume_output_dir() -> Path:
    """
    Get the directory where finished resume PDFs are written.

    Returns:
        Path to the resume output directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["output_dir"]


def get_resume_archive_dir() -> Path:
    """
    Get the directory where superseded resume PDFs are archived.

    Returns:
        Path to the resume archive/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["archive_dir"]


def get_resume_service_base_url() -> str:
    """
    Get the base URL of the local Reactive Resume service.

    Returns:
        Base URL, e.g. "http://localhost:3000".
    """
    props = get_properties()
    return props["resume"]["service"]["base_url"]


def get_resume_service_api_key() -> str:
    """
    Get the API key for the local Reactive Resume service.

    Returns:
        API key string (empty if not yet configured — see modules/employment/README.md).
    """
    props = get_properties()
    return props["resume"]["service"]["api_key"]


def get_resume_service_compose_dir() -> Path:
    """
    Get the directory holding the Reactive Resume Docker Compose files.

    Returns:
        Path to the compose directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["service"]["compose_dir"]
