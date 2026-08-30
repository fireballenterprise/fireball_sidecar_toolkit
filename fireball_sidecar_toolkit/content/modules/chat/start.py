"""Start a new research chat."""

import subprocess
from datetime import datetime

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.properties import get_repo_local, get_screenshots_location
from ..common.utils import error, get_active_topic_path, get_topic_path, success, validate_topics_directory
from .active import clear_active, create_slug, read_active, write_active


def _auto_end_active_chat(current_dir, active_data) -> None:
    """
    Automatically end the active chat (internal function).

    This handles the automatic ending when starting a new chat.
    """
    chat_filename = active_data.get("filename")
    chat_title = active_data.get("title", "chat")

    # Verify chat file exists
    chat_file = current_dir / "chats" / chat_filename
    if not chat_file.exists():
        error(f"Active chat file not found: {chat_filename}")

    click.echo("🔄 Auto-ending active chat to start new one...")
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


@click.command()
@click.option("--title", default=None, help="Title for the new chat")
def main(title: str | None = None) -> None:
    """
    Start a new research chat.

    Creates a new chat file with today's date and title.
    Tracks active chat in active.yml.
    Automatically ends any currently active chat first.
    """
    # Try to get active topic from active_topic.yml first
    active_topic_path = get_active_topic_path()

    if active_topic_path:
        # Use active topic from config
        current_dir = active_topic_path
    else:
        # Fall back to current working directory
        current_dir = get_original_cwd()
        validate_topics_directory(current_dir)

    # Prompt for title if not provided
    if not title:
        title = click.prompt("What would you like to title this chat?", type=str)

    if not title or not title.strip():
        error("Title cannot be empty")

    # Check for active chat and auto-end it
    existing_active = read_active(current_dir)
    if existing_active is not None:
        # Automatically end the active chat
        _auto_end_active_chat(current_dir, existing_active)

    # Get dates and create filename
    date_str = datetime.now().strftime("%Y%m%d")
    full_date = datetime.now().strftime("%B %d, %Y")
    slug = create_slug(title)
    filename = f"{date_str}_{slug}.md"

    # Create directories
    chats_dir = current_dir / "chats"
    chats_dir.mkdir(exist_ok=True)

    # Get topic path
    topic_path = get_topic_path(current_dir)

    # Create chat file
    chat_file = chats_dir / filename
    chat_content = f"""# {title}

Date: {full_date}
Topic: {topic_path}

## Overview

[This section will be filled in during the chat]

## Chat Log

"""
    chat_file.write_text(chat_content)

    # Create active.yml
    write_active(current_dir, filename, title, topic_path)

    # Configure screenshots
    screenshots_location = get_screenshots_location()
    screenshots_location.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["defaults", "write", "com.apple.screencapture", "location", str(screenshots_location)],
            check=True,
        )
        subprocess.run(["killall", "SystemUIServer"], check=False, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass  # Non-critical error

    # Success output
    success(f"New chat started: chats/{filename}")
    click.echo(f"✅ Screenshots configured: {screenshots_location}")
    click.echo("✅ Active chat tracked: active.yml")
    click.echo(f"✅ Topic: {topic_path}")
    click.echo()
    click.echo("Ready to begin research session.")
    click.echo("Use /chat start <new_title> to switch to a new chat, or /chat end when completely done.")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
