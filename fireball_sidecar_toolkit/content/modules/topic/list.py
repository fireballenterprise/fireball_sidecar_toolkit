"""List all topics in a tree/flat view, starring the active one. Backs `/topic list`."""

from __future__ import annotations

import logging

from ..common import cli as click
from . import active as topic_active
from . import update_list

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("--all", "show_all", is_flag=True, default=False, help="Show every topic instead of just the active one")
def main(show_all: bool = False) -> None:
    """Show the active topic, or every topic when `show_all` is set."""
    active = topic_active.get_active_topic()
    topics = update_list.list_topics()

    if not show_all:
        if active is None:
            click.echo("No active topic. Run `/topic switch <path>` or `/topic list all` to see every topic.")
            return
        click.echo(f"⭐ Active Topic: {active}")
        return

    if not topics:
        click.echo("No topics yet. Run `/topic new <path>` to create one.")
        return

    click.echo("📚 Available Topics")
    for topic in topics:
        marker = "⭐ " if topic == active else "  "
        click.echo(f"{marker}{topic}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
