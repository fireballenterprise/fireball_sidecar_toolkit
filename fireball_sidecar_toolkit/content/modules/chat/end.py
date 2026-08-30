"""End and save the current chat."""

import re

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.utils import error, get_active_topic_path, get_topic_path, success, validate_topics_directory
from .active import clear_active, read_active


def _validate_chat_context(chat_file) -> None:
    """Ensure chat file contains compact context and chat log entries."""
    try:
        content = chat_file.read_text()
    except OSError as e:
        error(f"Failed to read chat file for validation: {e}")

    has_overview = "## Overview" in content
    has_chat_log = "## Chat Log" in content
    has_placeholder = "[This section will be filled in during the chat]" in content
    has_log_entries = bool(re.search(r"\*\*\[\d{4}-\d{2}-\d{2} .*?\] (User|Assistant):\*\*", content))

    if has_overview and has_chat_log and not has_placeholder and has_log_entries:
        return

    click.echo("⚠️  Chat context is incomplete. /chat end requires saved context for future resume.")
    click.echo("Required before ending:")
    click.echo("  1. Update '## Overview' with a compact session summary")
    click.echo("  2. Append the complete conversation under '## Chat Log' with timestamps")
    click.echo()
    click.echo(f"Fix file: {chat_file}")
    error("Cannot end chat until context and chat log are saved")


@click.command()
def main() -> None:
    """
    End and save the current chat with full log.

    Validates that the complete chat context was saved to the chat file,
    then removes the active.yml tracker file to deactivate the session.
    Does not commit or push changes; use git commands explicitly when ready.
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

    # Get topic path
    topic_path = get_topic_path(current_dir)

    # Check for active chat
    active_data = read_active(current_dir)
    if active_data is None:
        click.echo("❌ No active chat found")
        click.echo()
        click.echo("💡 Use /chat start to begin a new chat or /chat resume to continue an existing one")
        raise SystemExit(0)

    chat_filename = active_data.get("filename") or ""

    # Verify chat file exists
    chat_file = current_dir / "chats" / chat_filename
    if not chat_file.exists():
        error(f"Chat file not found: {chat_filename}")

    _validate_chat_context(chat_file)

    # Remind user about chat log
    click.echo("⚠️  IMPORTANT: Make sure the AI agent has already appended the complete chat log!")
    click.echo("   The /chat end command validates that the full context was saved to the chat file.")
    click.echo("   The chat log should be formatted and saved BEFORE calling this command.")
    click.echo()
    click.echo(f"💾 Saving chat with full log: {chat_filename}")
    click.echo()

    # Remove active.yml
    clear_active(current_dir)
    click.echo("✅ Cleared active chat status")

    # Success output
    click.echo()
    success(f"Chat saved with full log: {chat_filename}")
    click.echo(f"📂 Topic: {topic_path}")
    click.echo()
    click.echo("📌 Changes saved to file but not committed to git.")
    click.echo("   Commit manually when ready (e.g., git add -A && git commit -m 'message')")
    click.echo()
    click.echo("💡 Tip: Start a new chat session with /chat start to clear context and reset tokens")
    click.echo("   Or use /chat resume to continue an existing chat")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
