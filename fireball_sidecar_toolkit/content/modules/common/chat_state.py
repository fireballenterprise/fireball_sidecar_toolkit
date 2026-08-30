"""
Shared read access to a topic's active.yml (chat state), used by both modules/chat/ (which owns
writing/clearing it) and modules/topic/switch.py (which only needs to peek at it before switching).
"""

from __future__ import annotations

from pathlib import Path

import yaml


def _normalize_active_data(data: object) -> dict | None:
    """Return validated active data or None if invalid."""
    if not isinstance(data, dict):
        return None

    filename = data.get("filename")
    title = data.get("title")
    topic = data.get("topic")

    if not isinstance(filename, str) or not filename.strip():
        return None
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(topic, str) or not topic.strip():
        return None

    normalized = dict(data)
    normalized["filename"] = filename.strip()
    normalized["title"] = title.strip()
    normalized["topic"] = topic.strip()

    status = normalized.get("status")
    if not isinstance(status, str) or not status.strip():
        normalized["status"] = "active"
    else:
        normalized["status"] = status.strip()

    return normalized


def read_active(topic_dir: Path) -> dict | None:
    """
    Read active.yml from topic directory.

    Args:
        topic_dir: Path to topic directory.

    Returns:
        Parsed active.yml data, or None if file does not exist.
    """
    active_file = topic_dir / "active.yml"
    if not active_file.exists():
        return None

    try:
        with active_file.open() as f:
            data = yaml.safe_load(f)
            return _normalize_active_data(data)
    except OSError:
        return None
    except yaml.YAMLError:
        return None
