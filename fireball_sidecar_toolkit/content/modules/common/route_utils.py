"""Shared helpers for slash-command routing modules (`modules/*/route.py`)."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def find_repo_root() -> Path:
    """Find repository root by locating properties.yml."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "properties.yml").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_active_topic_path(repo_root: Path) -> Path | None:
    """Read active_topic.yml and derive the absolute topic path from repo_root."""
    active_topic_file = repo_root / "active_topic.yml"
    if not active_topic_file.exists():
        return None

    try:
        with active_topic_file.open() as handle:
            data = yaml.safe_load(handle) or {}
    except OSError:
        return None
    except yaml.YAMLError:
        return None

    base_path = data.get("base_path")
    if base_path:
        return repo_root / base_path
    # Legacy state files stored an absolute machine path
    topic_full_path = data.get("topic_full_path")
    if not topic_full_path:
        return None
    return Path(topic_full_path)


def build_env(repo_root: Path) -> dict[str, str]:
    """Build environment with AI_VAULT_ORIGINAL_CWD if available."""
    env = os.environ.copy()
    active_topic = get_active_topic_path(repo_root)
    if active_topic:
        env["AI_VAULT_ORIGINAL_CWD"] = str(active_topic)
    return env
