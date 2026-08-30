"""Initialize a topic directory with AI instruction files."""

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.properties import get_repo_local, get_screenshots_location
from ..common.utils import error, info, success
from .templates import agents_md, claude_md
from .update_list import sync_from_filesystem


def _print_summary(topic_path: Path, screenshots_location: Path) -> None:
    """Print topic initialization summary."""
    click.echo()
    success("Topic initialization complete!")
    click.echo(f"📂 Topic: {topic_path}")
    click.echo("📁 Structure:")
    click.echo("  - chats/             (chat log files)")
    click.echo("  - docs/              (documentation and research)")
    click.echo("  - AGENTS.md          (AI agent instructions — Copilot, Codex, Cursor, etc.)")
    click.echo("  - CLAUDE.md          (AI agent instructions — Claude Code)")
    click.echo()
    click.echo("📸 Screenshots:")
    click.echo(f"  - Centralized location: {screenshots_location}")
    click.echo("  - All screenshots save to repo root (NOT topic-specific folders)")
    click.echo("  - Use 'ss' command to view latest screenshot")
    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  1. Customize the instruction files for this topic")
    click.echo("  2. Run /chat start to begin a chat")
    click.echo("  3. Use /chat end when done to save and sync everything")


@click.command()
@click.option("--description", "-d", default=None, help="Custom description for the topic")
def main(description: str | None = None) -> None:
    """
    Initialize a topic directory with AI instruction files.

    Must be run from within a topic directory under topics/.
    Creates chats/, docs/ directories and AGENTS.md / CLAUDE.md instruction files.
    """
    # Get original working directory (where user invoked the command)
    current_dir = get_original_cwd()
    repo_local = get_repo_local()
    topics_root = repo_local / "topics"

    click.echo("🚀 Topic Initialization")
    click.echo(f"📍 Current directory: {current_dir}")

    # Validate we're in a topic directory
    if not str(current_dir).startswith(str(topics_root)):
        error(
            f"Must be run from within a topic directory under topics/\n"
            f"💡 Current location: {current_dir}\n"
            f"💡 Expected: Inside {topics_root}"
        )

    # Get relative topic path
    topic_path = current_dir.relative_to(topics_root)
    info(f"Initializing topic: {topic_path}")

    # Create directories
    click.echo()
    click.echo("📁 Creating directories...")
    chats_dir = current_dir / "chats"
    chats_dir.mkdir(exist_ok=True)
    click.echo("  ✅ chats/")

    docs_dir = current_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    click.echo("  ✅ docs/")

    # Check for existing files and prompt
    existing_files = []
    agents_file = current_dir / "AGENTS.md"
    claude_file = current_dir / "CLAUDE.md"

    for fname, fpath in [("AGENTS.md", agents_file), ("CLAUDE.md", claude_file)]:
        if fpath.exists():
            existing_files.append(fname)

    if existing_files:
        click.echo()
        click.echo("⚠️  Warning: The following files already exist:")
        for file in existing_files:
            click.echo(f"  - {file}")
        click.echo()

        if not click.confirm("Overwrite existing files?"):
            click.echo("❌ Initialization cancelled. No files were modified.")
            return

    # Create AI instruction files
    click.echo()
    click.echo("📝 Creating AI instruction files...")

    # AGENTS.md (primary: Copilot, Codex, Cursor, etc.)
    agents_file.write_text(agents_md(str(topic_path), description, repo_root=repo_local))
    click.echo("  ✅ AGENTS.md")

    # CLAUDE.md (Claude Code)
    claude_file.write_text(claude_md(str(topic_path), description, repo_root=repo_local))
    click.echo("  ✅ CLAUDE.md")

    if description:
        click.echo(f"  💡 Using custom description: {description}")

    # Warn if parent folder is missing an AGENTS.md
    parent_agents_file = current_dir.parent / "AGENTS.md"
    if not parent_agents_file.exists() and current_dir.parent != topics_root:
        click.echo()
        click.echo(
            f"⚠️  Parent folder '{current_dir.parent.name}/' has no AGENTS.md.\n"
            f"   Consider creating one at: {parent_agents_file.relative_to(repo_local)}\n"
            "   Parent AGENTS.md files help AI agents navigate the topic tree."
        )

    # Ensure centralized screenshots folder exists at repo root
    click.echo()
    click.echo("📸 Ensuring centralized screenshots folder...")
    screenshots_location = get_screenshots_location()
    screenshots_location.mkdir(parents=True, exist_ok=True)

    # Configure macOS screenshot location to use centralized folder
    click.echo("Configuring macOS to save screenshots to centralized folder...")
    try:
        subprocess.run(
            ["defaults", "write", "com.apple.screencapture", "location", str(screenshots_location)],
            check=True,
        )
        subprocess.run(["killall", "SystemUIServer"], check=False, stderr=subprocess.DEVNULL)
        click.echo(f"  ✅ Screenshot location configured: {screenshots_location}")
        click.echo("  💡 All screenshots save to centralized repo location")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️  Warning: Could not configure screenshot location: {e}")

    # Keep topics/topics_list.yml in sync with newly initialized topic path.
    click.echo()
    click.echo("🗺️ Updating topics map...")
    if sync_from_filesystem(repo_local):
        click.echo("  ✅ topics/topics_list.yml updated")
    else:
        click.echo("  ✅ topics/topics_list.yml already up to date")

    _print_summary(topic_path, screenshots_location)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
