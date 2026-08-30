"""Active topic state management for repository root."""

from datetime import datetime
from pathlib import Path

import yaml

ACTIVE_TOPIC_YML_HEADER = "# Active topic tracker\n# Managed by topic/switch.py\n# Do not edit manually\n---\n"


def read_active_topic(repo_root: Path) -> str | None:
    """
    Read current topic path from active_topic.yml.

    Args:
        repo_root: Path to repository root.

    Returns:
        Current topic path string, or None if not set.
    """
    active_topic_file = repo_root / "active_topic.yml"
    if not active_topic_file.exists():
        return None

    try:
        with active_topic_file.open() as f:
            data = yaml.safe_load(f) or {}
        return data.get("current_topic")
    except OSError:
        return None
    except yaml.YAMLError:
        return None


def write_active_topic(repo_root: Path, topic_path: str) -> None:
    """
    Write active_topic.yml at repository root.

    Paths are stored repo-relative only — the absolute topic path is derived at
    read time from the repo root, so the file stays portable across machines.

    Args:
        repo_root: Path to repository root.
        topic_path: Relative topic path (e.g. workshop/tig_welding).
    """
    active_topic_file = repo_root / "active_topic.yml"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    active_topic_data = {
        "current_topic": topic_path,
        "base_path": f"topics/{topic_path}",
        "switched_at": timestamp,
    }

    with active_topic_file.open("w") as f:
        f.write(ACTIVE_TOPIC_YML_HEADER)
        yaml.dump(active_topic_data, f, default_flow_style=False)
