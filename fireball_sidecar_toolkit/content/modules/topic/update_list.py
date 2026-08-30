"""Sync topics_list.yml with all AGENTS.md files on disk."""

from pathlib import Path

import yaml

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import success


def sync_from_filesystem(repo_local: Path) -> bool:
    """
    Rebuild topics_list.yml from all AGENTS.md files on disk.

    Scans topics/ recursively for AGENTS.md files and builds a fully
    nested dict tree where an empty dict signals a leaf topic node.
    Writes only when content has changed.

    Args:
        repo_local: Absolute path to repo root.

    Returns:
        True if topics_list.yml was updated, False if already up to date.
    """
    topics_root = repo_local / "topics"
    topics_yaml = topics_root / "topics_list.yml"

    tree: dict = {}
    for agents_file in sorted(topics_root.rglob("AGENTS.md")):
        try:
            rel = agents_file.parent.relative_to(topics_root)
        except ValueError:
            continue
        node = tree
        for part in rel.parts:
            node = node.setdefault(part, {})

    new_content = yaml.dump({"topics_layout": tree}, default_flow_style=False, sort_keys=True)
    existing_content = topics_yaml.read_text() if topics_yaml.exists() else ""
    if existing_content == new_content:
        return False

    topics_yaml.write_text(new_content)
    return True


@click.command()
def main() -> None:
    """Sync topics_list.yml from all AGENTS.md files on disk."""
    repo_local = get_repo_local()
    click.echo("🔄 Syncing topics_list.yml from filesystem...")
    changed = sync_from_filesystem(repo_local)
    if changed:
        success("topics_list.yml updated")
    else:
        click.echo("✅ Already up to date")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
