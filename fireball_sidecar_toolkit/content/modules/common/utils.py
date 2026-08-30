"""Common utilities for AI research automation."""

import re
import sys
from pathlib import Path
from typing import NoReturn

import yaml


def success(message: str) -> None:
    """Print success message with emoji prefix."""
    print(f"✅ {message}")


def error(message: str, exit_code: int = 1) -> NoReturn:
    """Print error message to stderr and exit."""
    print(f"❌ {message}", file=sys.stderr)
    sys.exit(exit_code)


def warning(message: str) -> None:
    """Print warning message with emoji prefix."""
    print(f"⚠️ {message}")


def info(message: str) -> None:
    """Print info message with emoji prefix."""
    print(f"📂 {message}")


def target(message: str) -> None:
    """Print target message with emoji prefix."""
    print(f"🎯 {message}")


def camera(message: str) -> None:
    """Print camera/screenshot message with emoji prefix."""
    print(f"📸 {message}")


def create_slug(text: str) -> str:
    """
    Convert text to a URL/filename-safe slug.

    Lowercases the text, strips characters that are not alphanumeric, hyphens,
    or spaces, then collapses whitespace runs into single underscores.

    Args:
        text: The input string to slugify.

    Returns:
        A lowercase slug with spaces replaced by underscores.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text


def validate_topics_directory(current_path: Path | None = None) -> Path:
    """
    Validate that current directory is within topics/ subdirectory.

    Args:
        current_path: Path to validate. Defaults to current working directory.

    Returns:
        The validated path.

    Raises:
        SystemExit: If not in a topics/ directory.
    """
    if current_path is None:
        current_path = Path.cwd()

    if "/topics/" not in str(current_path):
        error(
            f"Error: Must be in a topic directory.\n"
            f"Current directory: {current_path}\n"
            f"Use /topic to navigate to a topic first."
        )

    return current_path


def get_topic_path(current_path: Path | None = None) -> str:
    """
    Extract topic path from current directory.

    Args:
        current_path: Path to extract from. Defaults to current working directory.

    Returns:
        Topic path relative to topics/ directory.

    Raises:
        SystemExit: If topic path cannot be extracted.
    """
    if current_path is None:
        current_path = Path.cwd()

    path_str = str(current_path)
    if "topics/" in path_str:
        return path_str.split("topics/", 1)[1]

    error("Could not extract topic path from current directory")


def get_active_topic_path() -> Path | None:
    """
    Get the active topic path from active_topic.yml.

    Returns:
        Path to the active topic directory, or None if no active topic.
    """
    # Find repo root by looking for active_topic.yml
    current = Path.cwd()
    while current != current.parent:
        active_topic_file = current / "active_topic.yml"
        if active_topic_file.exists():
            with active_topic_file.open() as f:
                data = yaml.safe_load(f) or {}
            base_path = data.get("base_path")
            if base_path:
                return current / base_path
            # Legacy state files stored an absolute machine path
            topic_full_path = data.get("topic_full_path")
            if topic_full_path:
                return Path(topic_full_path)
            return None
        current = current.parent
    return None
