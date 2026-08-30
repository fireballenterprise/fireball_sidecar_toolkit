"""Switch between topics or create new topics."""

import difflib

from ..common import cli as click
from ..common.chat_state import read_active as read_chat_active
from ..common.invoke_runner import get_original_cwd
from ..common.properties import get_repo_local
from ..common.utils import success
from .active import write_active_topic


@click.command()
@click.option("--path", required=True, help="Topic path (e.g., 'mac/fusion')")
def main(path: str) -> None:  # pylint: disable=too-many-branches,too-many-statements,too-many-locals,too-many-nested-blocks # noqa: C901, PLR0912, PLR0915
    """
    Switch to a different topic context or create new topic.

    Intelligently switches between topics with:
    - Fuzzy matching for typos
    - Auto-suggests similar topics
    - Offers to create new topics
    - Saves current chat automatically
    - Resumes active chat in new topic
    """
    repo_root = get_repo_local()

    topics_root = repo_root / "topics"
    target_topic = topics_root / path

    click.echo("🔄 Topic Switch")
    click.echo()

    # Validate topic exists or offer alternatives
    if not target_topic.exists():
        click.echo(f"❌ Topic '{path}' not found.")
        click.echo()

        # Find similar topics using fuzzy matching (support arbitrary depth)
        all_topics = []
        if topics_root.exists():

            def scan_topics(base_path):
                """Recursively scan for topic directories."""
                for item in base_path.iterdir():
                    if item.is_dir() and not item.name.startswith("."):
                        # Check if this directory has chats/ subdirectory (indicates it's a topic)
                        if (item / "chats").exists():
                            relative_path = item.relative_to(topics_root)
                            all_topics.append(str(relative_path))
                        else:
                            # Continue scanning deeper
                            scan_topics(item)

            scan_topics(topics_root)

        # Find close matches
        close_matches = difflib.get_close_matches(path, all_topics, n=3, cutoff=0.6)

        if close_matches:
            click.echo("Did you mean:")
            for i, match in enumerate(close_matches, 1):
                # Calculate similarity percentage
                similarity = difflib.SequenceMatcher(None, path, match).ratio()
                percentage = int(similarity * 100)

                # Try to get topic description from AGENTS.md
                topic_agents = topics_root / match / "AGENTS.md"
                topic_description = ""
                if topic_agents.exists():
                    try:
                        content = topic_agents.read_text()
                        # Extract topic name from first # header
                        for line in content.split("\n"):
                            if line.startswith("# "):
                                topic_description = line.replace("#", "").strip()
                                for prefix in (
                                    "your AI tool Instructions for ",
                                    "Claude Code Instructions for ",
                                    "AI Agent Instructions for ",
                                ):
                                    if topic_description.startswith(prefix):
                                        topic_description = topic_description.replace(prefix, "")
                                        break
                                break
                    except OSError:
                        pass
                    except UnicodeDecodeError:
                        pass

                if topic_description:
                    click.echo(f"  {i}. {match} ({percentage}% match) - {topic_description}")
                else:
                    click.echo(f"  {i}. {match} ({percentage}% match)")
            click.echo()

            best_match = close_matches[0]
            if click.confirm(f"Use '{best_match}' instead?", default=True):
                path = best_match
                target_topic = topics_root / path
                click.echo()
                click.echo(f"✅ Using existing topic: {path}")
                click.echo()
            else:
                click.echo()
                click.echo(f"💡 To create a new topic, run: /topic new {path}")
                return

        else:
            click.echo(f"💡 To create a new topic, run: /topic new {path}")
            return

    # Save current active chat if exists
    current_dir = get_original_cwd()
    active_data = read_chat_active(current_dir)

    if active_data is not None:
        chat_title = active_data.get("title", "chat")
        click.echo(f"💾 Saving current chat: {chat_title}")
        # Note: We're keeping the chat active in its topic
        # Just saving state, not ending the chat
        click.echo(f"✅ Chat remains active in current topic: {current_dir.name}")
        click.echo()

    # Update active_topic.yml tracker at repo root
    write_active_topic(repo_root, path)

    # Check for active chat in new topic
    new_active_data = read_chat_active(target_topic)
    has_active_chat = new_active_data is not None

    active_chat_info = ""
    if has_active_chat:
        chat_title = new_active_data.get("title", "unknown")
        chat_filename = new_active_data.get("filename", "unknown")
        active_chat_info = f"🔄 Active chat: {chat_title} ({chat_filename})"

    # Success output
    success(f"Switched to: {path}")
    click.echo(f"📂 Base path: topics/{path}")
    click.echo(f"📍 Full path: {target_topic}")
    click.echo()

    if has_active_chat:
        click.echo(active_chat_info)
        click.echo("   → Chat will resume automatically")
    else:
        click.echo("📝 No active chat in this topic")
        click.echo("   → Use /chat start to begin a new chat")

    click.echo()
    click.echo("━" * 60)
    click.echo()
    click.echo("💡 IMPORTANT: For cleanest AI context separation:")
    click.echo("   1. Run /new (clears conversation history)")
    click.echo("   2. Run /topic again to load fresh context")
    click.echo()
    click.echo("Or continue - AI will prioritize new topic context.")
    click.echo()
    click.echo("📖 AI should now read:")
    click.echo(f"   - {repo_root}/AGENTS.md")
    click.echo(f"   - {target_topic}/AGENTS.md")
    click.echo()
    click.echo("Ready to work on this topic!")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
