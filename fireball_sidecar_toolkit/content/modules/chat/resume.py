"""Resume an existing chat."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.properties import get_repo_local
from ..common.utils import error, get_active_topic_path, get_topic_path, success, validate_topics_directory
from .active import clear_active, read_active, write_active


def _auto_end_active_chat(current_dir: Path, active_data: dict) -> None:
    """
    Automatically end the active chat (internal function).

    This handles the automatic ending when resuming a different chat.
    """
    chat_filename = active_data.get("filename", "")
    chat_title = active_data.get("title", "chat")

    # Verify chat file exists
    chat_file = current_dir / "chats" / chat_filename
    if not chat_file.exists():
        error(f"Active chat file not found: {chat_filename}")

    click.echo("🔄 Auto-ending active chat to resume another...")
    click.echo(f"   Saving: {chat_filename} ({chat_title})")

    # Get repo root
    repo_root = get_repo_local()

    # Stage all changes
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error(f"Failed to stage changes: {e}")

    # Generate commit message
    message = f"Research session: {chat_title}"

    # Commit changes
    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo("   ✅ Changes committed")
    except subprocess.CalledProcessError as e:
        # Check if there were no changes to commit
        if "nothing to commit" not in e.stdout and "nothing to commit" not in e.stderr:
            error(f"Failed to commit changes: {e.stderr}")
        # If nothing to commit, that's fine - continue

    click.echo("   📌 Changes saved locally (run /push when ready)")

    # Remove active.yml
    clear_active(current_dir)
    click.echo("   ✅ Cleared previous active chat status")

    click.echo()


def _get_topic_dir() -> Path:
    active_topic_path = get_active_topic_path()
    if active_topic_path:
        return active_topic_path

    current_dir = get_original_cwd()
    validate_topics_directory(current_dir)
    return current_dir


def _load_chat_files(topic_dir: Path, topic_path: str, pattern: str | None) -> list[Path]:
    chats_dir = topic_dir / "chats"
    if not chats_dir.exists():
        click.echo()
        click.echo("💡 Use /chat start to create your first chat")
        error(f"No chats found in topic: {topic_path}")

    chat_files = list(chats_dir.glob("*.md"))
    if not chat_files:
        click.echo()
        click.echo("💡 Use /chat start to create your first chat")
        error(f"No chats found in topic: {topic_path}")

    if not pattern:
        chat_files.sort(reverse=True)
        return chat_files

    matching_files = [f for f in chat_files if pattern.lower() in f.name.lower()]
    if not matching_files and " " in pattern:
        underscored_pattern = pattern.replace(" ", "_")
        matching_files = [f for f in chat_files if underscored_pattern.lower() in f.name.lower()]

    if not matching_files:
        error(f"No chats found matching: {pattern}")

    matching_files.sort(reverse=True)
    return matching_files


def _select_chat_file(chat_files: list[Path], topic_path: str) -> Path:
    if len(chat_files) == 1:
        return chat_files[0]

    click.echo(f"📂 Available chats in {topic_path}:")
    click.echo()
    for idx, conv_file in enumerate(chat_files, 1):
        click.echo(f"{idx}. {conv_file.name}")
        try:
            content = conv_file.read_text()
            lines = content.split("\n")
            if lines:
                title_line = lines[0].replace("#", "").strip()
                if title_line:
                    click.echo(f"   {title_line}")
        except OSError:
            pass
        except UnicodeDecodeError:
            pass
        click.echo()

    selection = click.prompt("Select chat number to resume", type=click.IntRange(1, len(chat_files)))
    return chat_files[selection - 1]


def _extract_title(chat_file: Path) -> str:
    try:
        content = chat_file.read_text()
    except OSError:
        return chat_file.stem

    lines = content.split("\n")
    if not lines:
        return chat_file.stem

    first = lines[0].replace("#", "").strip()
    return first or chat_file.stem


def _print_chat_preview(chat_file: Path) -> None:
    """Print a short preview to help continue the conversation."""
    try:
        content = chat_file.read_text()
    except OSError:
        return

    preview_lines = [line for line in content.splitlines() if line.strip()][:6]
    if not preview_lines:
        return

    click.echo("📖 Chat preview:")
    for line in preview_lines:
        click.echo(f"   {line}")
    click.echo()


@click.command()
@click.option("--pattern", default=None, help="Search pattern to filter chats")
def main(pattern: str | None = None) -> None:
    """
    Resume an existing chat.

    If pattern provided, searches for matching chat files.
    If no pattern, prompts user to select from available chats.
    Updates active.yml to track the resumed chat.
    """
    topic_dir = _get_topic_dir()
    topic_path = get_topic_path(topic_dir)

    # Check for active chat and auto-end it if resuming a different chat
    existing_active = read_active(topic_dir)
    if existing_active is not None:
        # Automatically end the active chat
        _auto_end_active_chat(topic_dir, existing_active)

    chat_files = _load_chat_files(topic_dir, topic_path, pattern)
    selected_file = _select_chat_file(chat_files, topic_path)
    title = _extract_title(selected_file)
    write_active(topic_dir, selected_file.name, title, topic_path, resumed=True)

    # Success output
    success(f"Resumed chat: {selected_file.name}")
    click.echo("✅ Active chat tracked: active.yml")
    click.echo(f"✅ Topic: {topic_path}")
    click.echo()
    _print_chat_preview(selected_file)
    click.echo("You can now continue this chat.")
    click.echo("Use /chat end when done to save and clear active status.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
