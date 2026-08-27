"""Properties management for repo automation."""

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


def get_template_local() -> Path:
    """
    Get the local path to the shared template repo (template_python), used by /template.

    A relative path is resolved against this repo's root.

    Returns:
        Path to the template repository.
    """
    props = get_properties()
    local = _expand_path(props["template"]["local"])
    return local if local.is_absolute() else get_repo_root() / local


def get_template_remote() -> str:
    """
    Get the template repo's remote (e.g. "github.com/LevonBecker/template_python").

    Returns:
        Remote repository reference, without a URL scheme.
    """
    props = get_properties()
    return props["template"]["remote"]
