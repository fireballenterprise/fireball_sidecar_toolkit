"""Common utilities for repo automation."""

import sys
from typing import NoReturn


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
