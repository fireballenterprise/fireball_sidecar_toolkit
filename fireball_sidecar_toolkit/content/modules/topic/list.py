"""Display topics in pretty tree format."""

from __future__ import annotations

from typing import Any

import yaml

from ..common import cli as click
from ..common.properties import get_repo_local
from ..common.utils import error
from .active import read_active_topic


def _print_tree(tree: dict[str, Any], active_topic: str | None) -> None:
    for category in sorted(tree.keys()):
        children = tree[category]
        star = "⭐ " if active_topic == category else ""
        click.secho(f"{star}{category}/", fg="cyan", bold=True)
        _print_tree_node(children, active_topic, parent_path=category, indent="  ")


def _print_tree_node(tree: dict[str, Any], active_topic: str | None, parent_path: str, indent: str) -> None:
    for key in sorted(tree.keys()):
        children = tree[key]
        current_path = f"{parent_path}/{key}"
        if children:
            star = "⭐ " if active_topic == current_path else ""
            click.secho(f"{indent}{star}{key}/", fg="yellow", bold=True)
            _print_tree_node(children, active_topic, parent_path=current_path, indent=indent + "  ")
        else:
            star = "⭐ " if active_topic == current_path else ""
            click.secho(f"{indent}├─ {star}{key}", fg="green")


@click.command()
@click.option("--all", "show_all", is_flag=True, help="Show the full topics tree")
def main(show_all: bool = False) -> None:
    """Display the active topic or the full topic tree."""
    repo_local = get_repo_local()
    topics_yaml = repo_local / "topics" / "topics_list.yml"
    active_topic = read_active_topic(repo_local)

    if not topics_yaml.exists():
        error("topics_list.yml not found. Run /topic update to generate it.")

    with topics_yaml.open() as f:
        data = yaml.safe_load(f) or {}

    topics_layout = data.get("topics_layout")
    if not isinstance(topics_layout, dict):
        error("Invalid topics_list.yml format: missing or invalid 'topics_layout' key")

    if not show_all:
        if active_topic:
            click.echo(f"⭐ Active Topic: {active_topic}")
        else:
            click.echo("No active topic is currently set.")

        click.echo()
        click.echo("💡 Use /topic list all to show all topics")
        click.echo("💡 Use /topic <path> to navigate to a topic")
        click.echo("   Example: /topic mac/fusion")
        return

    click.echo("📚 Available Topics")
    click.echo("==================")
    click.echo()

    if active_topic:
        click.echo(f"⭐ Active Topic: {active_topic}")
        click.echo()

    _print_tree(topics_layout, active_topic)

    click.echo()
    click.echo("💡 Use /topic <path> to navigate to a topic")
    click.echo("   Example: /topic mac/fusion")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
