"""List chats in the current topic."""

import re

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.utils import error, get_active_topic_path, get_topic_path, info, validate_topics_directory
from .active import read_active


def _parse_filename(name: str) -> tuple[str, str]:
    """Return (date_str, title) parsed from YYYYMMDD_slug.md filename."""
    stem = name[:-3] if name.endswith(".md") else name
    match = re.match(r"^(\d{4})(\d{2})(\d{2})_(.*)", stem)
    if match:
        date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        title = match.group(4).replace("_", " ")
    else:
        date_str = ""
        title = stem.replace("_", " ")
    return date_str, title


def _print_row(num: str, date: str, title: str, flag: str = "") -> None:
    flag_col = f"  {flag}" if flag else ""
    click.echo(f"  {num:<4} {date:<12} {title}{flag_col}")


@click.command()
@click.option(
    "--sort",
    type=click.Choice(["newest_first", "oldest_first", "alphabetical"]),
    default="newest_first",
    help="Sort order for chats",
)
def main(sort: str) -> None:
    """
    List all chats in the current topic as a table, active chat shown last.
    """
    active_topic_path = get_active_topic_path()

    if active_topic_path:
        current_dir = active_topic_path
        topic_path = get_topic_path(current_dir)
    else:
        current_dir = get_original_cwd()
        validate_topics_directory(current_dir)
        topic_path = get_topic_path(current_dir)

    chats_dir = current_dir / "chats"
    if not chats_dir.exists():
        click.echo()
        click.echo("💡 Use /chat start to create your first chat")
        error(f"No chats found in topic: {topic_path}")

    chat_files = list(chats_dir.glob("*.md"))
    if not chat_files:
        click.echo()
        click.echo("💡 Use /chat start to create your first chat")
        error(f"No chats found in topic: {topic_path}")

    if sort == "newest_first":
        chat_files.sort(reverse=True)
    elif sort == "oldest_first":
        chat_files.sort()
    elif sort == "alphabetical":
        chat_files.sort(key=lambda x: x.name)

    active_data = read_active(current_dir)
    active_filename = active_data.get("filename") if active_data else None

    # Split into non-active and active
    non_active = [f for f in chat_files if f.name != active_filename]
    active_file = next((f for f in chat_files if f.name == active_filename), None)

    total = len(chat_files)
    click.echo(f"\n📂 Chats in {topic_path} ({total} total)\n")
    click.echo(f"  {'#':<4} {'Date':<12} Title")
    click.echo(f"  {'─' * 4} {'─' * 11} {'─' * 36}")

    for i, f in enumerate(non_active, start=1):
        date_str, title = _parse_filename(f.name)
        _print_row(str(i), date_str, title)

    # Active chat at the bottom
    if active_file:
        click.echo(f"  {'─' * 55}")
        date_str, title = _parse_filename(active_file.name)
        _print_row(str(len(non_active) + 1), date_str, title, "⭐ active")

    click.echo()
    info(f"Total: {total} chat{'s' if total != 1 else ''}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
