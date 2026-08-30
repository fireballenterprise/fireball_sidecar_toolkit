"""Update topic directories with latest templates and ensure required structure."""

from pathlib import Path

from ..common import cli as click
from ..common.invoke_runner import get_original_cwd
from ..common.properties import get_repo_local
from ..common.utils import error, info, success, warning
from .templates import agents_md, claude_md
from .update_list import sync_from_filesystem


def _get_topic_path(agents_file: Path, topics_root: Path) -> str:
    """
    Derive relative topic path string from an AGENTS.md file path.

    Args:
        agents_file: Absolute path to an AGENTS.md file.
        topics_root: Absolute path to topics/ directory.

    Returns:
        Relative topic path string (e.g. mac/fusion).
    """
    return str(agents_file.parent.relative_to(topics_root))


def _regenerate_agents(file_path: Path, topic_path: str, dry_run: bool) -> bool:
    """
    Regenerate AGENTS.md and CLAUDE.md from the canonical templates.

    Compares full content — only writes if different. Regenerates both
    instruction files so they stay in sync across AI tools.

    Args:
        file_path: Absolute path to AGENTS.md file.
        topic_path: Relative topic path (e.g. mac/fusion).
        dry_run: If True, report changes without writing.

    Returns:
        True if any file was (or would be) updated, False if all are already current.
    """
    try:
        topic_dir = file_path.parent
        updated = False

        generators = [
            (file_path, agents_md(topic_path)),
            (topic_dir / "CLAUDE.md", claude_md(topic_path)),
        ]

        for target_path, new_content in generators:
            existing_content = target_path.read_text() if target_path.exists() else ""
            if existing_content != new_content:
                if not dry_run:
                    target_path.write_text(new_content)
                updated = True

        return updated

    except (OSError, UnicodeDecodeError) as e:
        error(f"Failed to update {file_path}: {e}")


def _ensure_dirs(topic_dir: Path, dry_run: bool) -> list[str]:
    """
    Create missing chats/ and docs/ directories in a topic directory.

    Args:
        topic_dir: Absolute path to topic directory.
        dry_run: If True, report without creating.

    Returns:
        List of directory names that were (or would be) created.
    """
    created = []
    for dirname in ("chats", "docs"):
        target = topic_dir / dirname
        if not target.exists():
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)
            created.append(dirname)
    return created


def _find_agent_files(start_path: Path) -> list[Path]:
    """
    Find all AGENTS.md files under the given path.

    Args:
        start_path: Directory to search recursively.

    Returns:
        Sorted list of AGENTS.md file paths.
    """
    if start_path.name == "AGENTS.md" and start_path.is_file():
        return [start_path]
    if start_path.is_dir():
        return sorted(start_path.rglob("AGENTS.md"))
    return []


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without making changes",
)
@click.option(
    "--current-only",
    is_flag=True,
    help="Only update the current topic directory",
)
@click.option(
    "--working-dir",
    type=click.Path(exists=True),
    default=None,
    help="Working directory override",
)
def main(dry_run: bool, current_only: bool, working_dir: str | None) -> None:
    """
    Update topic directories with latest AI instruction templates and ensure chats/ and docs/ exist.

    Regenerates AGENTS.md and CLAUDE.md from the canonical templates
    (full content replacement). Creates missing chats/ and docs/ directories.
    Can update all topics or just the current one.
    """
    repo_root = get_repo_local()
    topics_dir = repo_root / "topics"

    if working_dir:
        current_dir = Path(working_dir)
    else:
        try:
            current_dir = get_original_cwd()
        except KeyError:
            current_dir = Path.cwd()
        except ValueError:
            current_dir = Path.cwd()

    click.echo("🔄 Updating topic directories")
    click.echo()

    if dry_run:
        warning("Dry run mode - no changes will be written")
        click.echo()

    # Determine which files to process
    if current_only:
        try:
            rel_path = current_dir.relative_to(topics_dir)
        except ValueError:
            click.echo()
            click.echo("💡 Run from within a topic directory, or omit --current-only to update all")
            error("Current directory is not within topics/")

        agents_file = current_dir / "AGENTS.md"
        if not agents_file.exists():
            error(f"No AGENTS.md found in: {current_dir}")

        files_to_process = [agents_file]
        info(f"Updating current topic: {rel_path}")
    else:
        files_to_process = _find_agent_files(topics_dir)
        info(f"Found {len(files_to_process)} AGENTS.md files")

    click.echo()

    updated_count = 0
    unchanged_count = 0
    dirs_created: list[str] = []

    for file_path in files_to_process:
        rel_path = file_path.relative_to(repo_root)
        topic_path = _get_topic_path(file_path, topics_dir)

        # Regenerate AGENTS.md + CLAUDE.md
        if _regenerate_agents(file_path, topic_path, dry_run):
            success(f"{'Would update' if dry_run else 'Updated'}: {rel_path}")
            updated_count += 1
        else:
            unchanged_count += 1

        # Ensure chats/ and docs/ exist
        created = _ensure_dirs(file_path.parent, dry_run)
        for dirname in created:
            verb = "Would create" if dry_run else "Created"
            click.echo(f"  📁 {verb}: {rel_path.parent}/{dirname}/")
            dirs_created.append(f"{topic_path}/{dirname}")

    # Summary
    click.echo()
    click.echo("━" * 50)

    if dry_run:
        info(f"Would update: {updated_count} files")
        info(f"No changes needed: {unchanged_count} files")
        if dirs_created:
            info(f"Would create: {len(dirs_created)} directories")
        click.echo()
        click.echo("💡 Run without --dry-run to apply changes")
    else:
        success(f"Updated: {updated_count} files")
        if unchanged_count > 0:
            info(f"Already up to date: {unchanged_count} files")
        if dirs_created:
            success(f"Created: {len(dirs_created)} directories")
        click.echo()
        click.echo("✅ Topic directories update complete")
        click.echo()
        # Sync topics_list.yml to match current filesystem state
        if sync_from_filesystem(repo_root):
            success("topics_list.yml synced")
        else:
            info("topics_list.yml already up to date")
        click.echo()
        click.echo("💡 Run '/push' to commit and push these changes")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
