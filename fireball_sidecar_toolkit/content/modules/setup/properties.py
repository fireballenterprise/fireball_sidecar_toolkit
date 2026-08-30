"""Properties management for AI research repository."""

import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..common import cli
from ..common.utils import info, success


def _expand_path(value: str) -> Path:
    """Expand ~ and environment variables (e.g. $HOME) in a properties.yml path value."""
    return Path(os.path.expandvars(os.path.expanduser(value)))


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    """
    Find repository root by searching upward for properties.yml.

    Works from any subdirectory within the repository.

    Returns:
        Path to repository root.

    Raises:
        FileNotFoundError: If properties.yml cannot be found.
    """
    # Start from current file location
    current = Path(__file__).resolve()

    # Search upward from current file location
    for parent in [current.parent.parent.parent] + list(current.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    # Also try from current working directory
    current_cwd = Path.cwd().resolve()
    for parent in [current_cwd] + list(current_cwd.parents):
        props_file = parent / "properties.yml"
        if props_file.exists():
            return parent

    msg = "Could not find repository root (properties.yml not found)"
    raise FileNotFoundError(msg)


@lru_cache(maxsize=1)
def get_properties() -> dict[str, Any]:
    """
    Load properties.yml with singleton pattern (cached).

    Returns:
        Dictionary with all repository properties.

    Raises:
        FileNotFoundError: If properties.yml does not exist.
    """
    repo_root = get_repo_root()
    props_file = repo_root / "properties.yml"

    with props_file.open() as f:
        return yaml.safe_load(f)


def get_repo_local() -> Path:
    """
    Get repo local path as Path object.

    Returns:
        Path to local repository.
    """
    props = get_properties()
    return _expand_path(props["repo"]["local"])


def get_repo_remote() -> str:
    """
    Get repo remote URL.

    Returns:
        Remote repository URL.
    """
    props = get_properties()
    return props["repo"]["remote"]


def is_icloud_enabled() -> bool:
    """
    Whether iCloud-Obsidian sync is turned on for /push and /pull.

    Off by default. Missing `icloud` section or `icloud.enabled` → False.

    Returns:
        True when `icloud.enabled` is truthy in properties.yml.
    """
    props = get_properties()
    return bool(props.get("icloud", {}).get("enabled", False))


def get_icloud_path() -> Path:
    """
    Get iCloud sync path as Path object.

    Returns:
        Path to iCloud sync location.
    """
    props = get_properties()
    return _expand_path(props["icloud"]["path"])


def get_screenshots_location() -> Path:
    """
    Get screenshots directory path as Path object.

    Returns:
        Path to screenshots directory.
    """
    props = get_properties()
    return _expand_path(props["screenshots"]["location"])


def get_screenshots_latest_file() -> str:
    """
    Get latest screenshot filename.

    Returns:
        Filename for latest screenshot.
    """
    props = get_properties()
    return props["screenshots"]["latest_file"]


def get_screenshots_preserve_files() -> list[str]:
    """
    Get list of screenshot files to preserve during cleanup.

    Returns:
        List of filenames to preserve.
    """
    props = get_properties()
    return props["screenshots"]["preserve_files"]


def get_screenshots_cleanup_patterns() -> list[str]:
    """
    Get list of file patterns to clean up.

    Returns:
        List of glob patterns for cleanup.
    """
    props = get_properties()
    return props["screenshots"]["cleanup_patterns"]


def get_card_progress_csv() -> Path:
    """
    Get card progress CSV path.

    Returns:
        Path to card progress CSV file.
    """
    props = get_properties()
    repo_local = get_repo_local()
    csv_path = props["financials"]["card_progress_csv"]
    return repo_local / csv_path


def get_resume_work_history_md() -> Path:
    """
    Get path to the employment work history markdown file (raw resume source material).

    Returns:
        Path to work_history.md.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["work_history_md"]


def get_resume_guidelines_md() -> Path:
    """
    Get path to the resume guidelines markdown file (filtering/positioning strategy).

    Returns:
        Path to resume_guidelines.md.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["guidelines_md"]


def get_resume_raw_dir() -> Path:
    """
    Get the directory where in-progress raw resume drafts (JSON) are written.

    Returns:
        Path to the resume raw/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["raw_dir"]


def get_resume_templates_dir() -> Path:
    """
    Get the directory holding reusable resume starting templates (JSON).

    Returns:
        Path to the resume templates/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["templates_dir"]


def get_resume_output_dir() -> Path:
    """
    Get the directory where finished resume PDFs are written.

    Returns:
        Path to the resume output directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["output_dir"]


def get_resume_archive_dir() -> Path:
    """
    Get the directory where superseded resume PDFs are archived.

    Returns:
        Path to the resume archive/ directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["archive_dir"]


def get_resume_service_base_url() -> str:
    """
    Get the base URL of the local Reactive Resume service.

    Returns:
        Base URL, e.g. "http://localhost:3000".
    """
    props = get_properties()
    return props["resume"]["service"]["base_url"]


def get_resume_service_api_key() -> str:
    """
    Get the API key for the local Reactive Resume service.

    Returns:
        API key string (empty if not yet configured — see modules/employment/README.md).
    """
    props = get_properties()
    return props["resume"]["service"]["api_key"]


def get_resume_service_compose_dir() -> Path:
    """
    Get the directory holding the Reactive Resume Docker Compose files.

    Returns:
        Path to the compose directory.
    """
    props = get_properties()
    repo_local = get_repo_local()
    return repo_local / props["resume"]["service"]["compose_dir"]


# --- properties.yml bootstrap (first-run writer) -------------------------------------------
# This module is clobbered to modules/toolkit/setup/ ; the tier fragments are repo-local.
# get_repo_root() can't be used here — it searches for properties.yml, which doesn't exist yet.
# This module is clobbered to modules/toolkit/setup/ ; the tier fragments stay repo-local (they
# come from the parent repos in the lineage — template_python, template_ai_vault, …).
_REPO_ROOT = Path(__file__).resolve().parents[3]
_PROPERTIES_FILE = _REPO_ROOT / "properties.yml"
_TEMPLATES_DIR = _REPO_ROOT / "modules" / "setup" / "templates" / "properties"


def _extract_repos_block(text: str) -> tuple[str, dict[str, Any] | None]:
    """Split a top-level `repos:` block out of raw YAML text.

    Returns (text with that block removed, its parsed value) — or (text, None) if there's no
    `repos:` block (a flow-style `repos: {}` placeholder doesn't count as one to extract).
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.rstrip("\n") == "repos:":
            end = i + 1
            while end < len(lines) and (not lines[end].strip() or lines[end][0].isspace()):
                end += 1
            block = "".join(lines[i:end])
            remaining = "".join(lines[:i] + lines[end:])
            return remaining, yaml.safe_load(block)["repos"]
    return text, None


def _merge_repos(accumulated: dict[str, Any], addition: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge one tier's repos contribution into the map accumulated from earlier tiers.

    Org lists are extended (no duplicates); `lineage` (parent -> children adjacency) is merged key
    by key, extending each parent's child list (no duplicates).
    """
    merged = {org: list(names) for org, names in accumulated.items() if org != "lineage"}
    lineage = {parent: list(children) for parent, children in accumulated.get("lineage", {}).items()}
    for org, names in addition.items():
        if org == "lineage":
            for parent, children in names.items():
                lineage.setdefault(parent, [])
                for child in children:
                    if child not in lineage[parent]:
                        lineage[parent].append(child)
            continue
        merged.setdefault(org, [])
        for name in names:
            if name not in merged[org]:
                merged[org].append(name)
    if lineage:
        merged["lineage"] = lineage
    return merged


def _lineage_depth(name: str, lineage: dict[str, list[str]]) -> int:
    """Return how many lineage hops bare repo `name` is from its root (0 for a root itself)."""
    parent_of = {child: parent for parent, children in lineage.items() for child in children}
    depth = 0
    current = name
    seen: set[str] = set()
    while current in parent_of and current not in seen:
        seen.add(current)
        current = parent_of[current]
        depth += 1
    return depth


def _render_lineage_children(names: list[str], lineage: dict[str, list[str]], indent: int) -> list[str]:
    """Render one level of the lineage tree: a leaf as `- name`, a parent as `- name:` + children.

    A nested sequence under a `- name:` list item must yamllint-indent 4 past that item's own dash
    (2 for the item's own key text, +2 more for its child sequence) rather than the usual 2.
    """
    pad = " " * indent
    lines = []
    for name in sorted(names):
        children = lineage.get(name)
        if children:
            lines.append(f"{pad}- {name}:")
            lines.extend(_render_lineage_children(children, lineage, indent + 4))
        else:
            lines.append(f"{pad}- {name}")
    return lines


def _render_repos_block(repos: dict[str, Any]) -> str:
    """Render a merged repos dict back into this file's hand-formatted YAML block style.

    Each org's list is ordered root-to-leaf by lineage depth, regardless of merge order. `lineage`
    renders as a nested parent -> children tree (see repos.instructions.md).
    """
    lineage: dict[str, list[str]] = repos.get("lineage", {})
    lines = ["repos:"]
    for org, names in repos.items():
        if org == "lineage":
            continue
        ordered = sorted(names, key=lambda name: _lineage_depth(name, lineage))
        lines.append(f"  {org}:")
        lines.extend(f"    - {name}" for name in ordered)
    if lineage:
        children_names = {child for children in lineage.values() for child in children}
        roots = sorted(name for name in lineage if name not in children_names)
        lines.append("  lineage:")
        for root in roots:
            lines.append(f"    {root}:")
            lines.extend(_render_lineage_children(lineage[root], lineage, indent=6))
    return "\n".join(lines) + "\n"


def _build_initial_content() -> str:
    """Assemble a fresh properties.yml from every tier fragment under templates/properties/*.yml.

    Each fragment's own `repos` contribution is deep-merged into the accumulated map (see module
    docstring) rather than concatenated; every other section is appended as raw text, ordered
    root-to-leaf by lineage depth regardless of filename/glob order.
    """
    repos: dict[str, Any] = {}
    fragments: list[tuple[str, str]] = []
    for template_file in sorted(_TEMPLATES_DIR.glob("*.yml")):
        remaining, template_repos = _extract_repos_block(template_file.read_text())
        if template_repos:
            repos = _merge_repos(repos, template_repos)
        if remaining.strip():
            fragments.append((template_file.stem, remaining.rstrip("\n")))

    lineage = repos.get("lineage", {})
    fragments.sort(key=lambda item: _lineage_depth(item[0], lineage))

    parts = [_render_repos_block(repos).rstrip("\n")]
    parts.extend(text for _, text in fragments)
    return "---\n\n" + "\n\n".join(parts) + "\n"


def _detect_repo_local() -> str:
    """Return this repo's absolute path, with $HOME swapped in for portability."""
    home = str(Path.home())
    repo_str = str(_REPO_ROOT)
    if repo_str.startswith(home):
        return "$HOME" + repo_str[len(home) :]
    return repo_str


def _detect_repo_remote() -> str | None:
    """Return the git origin remote as 'host/user/repo', or None if there isn't one."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    url = result.stdout.strip()
    url = re.sub(r"^git@([^:]+):", r"\1/", url)
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"\.git$", "", url)
    return url


def _read_scalar(lines: list[str], section: str, key: str) -> str | None:
    """Return the unquoted value of `key:` within a top-level `section:` block, or None."""
    in_section = False
    for line in lines:
        if line.rstrip("\n") == f"{section}:":
            in_section = True
            continue
        if not in_section:
            continue
        if line.strip() and not line[0].isspace():
            return None  # reached the next top-level key without finding it
        match = re.match(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", line)
        if match:
            return match.group(1).strip('"')
    return None


def _replace_scalar(lines: list[str], section: str, key: str, value: str, *, quote: bool = True) -> bool:
    """Rewrite `key: ...` to `key: value` within a top-level `section:` block, in place."""
    formatted = f'"{value}"' if quote else value
    in_section = False
    for i, line in enumerate(lines):
        if line.rstrip("\n") == f"{section}:":
            in_section = True
            continue
        if not in_section:
            continue
        if line.strip() and not line[0].isspace():
            return False  # reached the next top-level key without finding it
        match = re.match(rf"^(\s*{re.escape(key)}:\s*).*$", line)
        if match:
            lines[i] = f"{match.group(1)}{formatted}\n"
            return True
    return False


def _has_section(lines: list[str], section: str) -> bool:
    """Return whether a top-level `section:` block exists (e.g. a tier fragment that wasn't present)."""
    return any(line.rstrip("\n") == f"{section}:" for line in lines)


def _is_template_repo(repo_remote: str | None) -> bool:
    """Return whether this repo is itself a template (vs. a real repo forked from one).

    Every template repo in this family is named `template_*` (template_python, template_ai_python,
    template_ai_vault, template_shopify, ...) — checked against the git remote when available,
    falling back to the local folder name so it still works before a remote is set.
    """
    name = repo_remote.rsplit("/", 1)[-1] if repo_remote else _REPO_ROOT.name
    return name.startswith("template_")


def _sync_gitignore_tracking(repo_remote: str | None) -> None:
    """Strip properties.yml's ignore line from .gitignore for a real (non-template) repo.

    Template repos always keep properties.yml gitignored — see the module docstring. A repo
    forked from one should commit it instead, so this removes the ignore line (and its
    explanatory comment) the first time setup runs there. Idempotent: a repo that's already had
    the line removed, or never had it, is left untouched.
    """
    gitignore = _REPO_ROOT / ".gitignore"
    if not gitignore.exists() or _is_template_repo(repo_remote):
        return

    text = gitignore.read_text()
    if "/properties.yml" not in text:
        return

    kept = [
        line
        for line in text.splitlines()
        if line.strip() != "/properties.yml" and "generated by `inv setup.properties`" not in line
    ]
    collapsed: list[str] = []
    for line in kept:
        if line == "" and collapsed and collapsed[-1] == "":
            continue  # the removal above left two blank lines in a row — keep just one
        collapsed.append(line)
    gitignore.write_text("\n".join(collapsed) + "\n")
    success("properties.yml is no longer gitignored — commit it along with the rest of setup")


def _prompt_icloud_enabled(lines: list[str]) -> None:
    """Ask (interactively) whether to turn on iCloud sync for a freshly created properties.yml."""
    enabled = cli.confirm(
        "Enable iCloud sync for /push and /pull? (most people don't need this — off by default)",
        default=False,
    )
    _replace_scalar(lines, "icloud", "enabled", "true" if enabled else "false", quote=False)
    if enabled:
        info("iCloud sync enabled — edit icloud.path in properties.yml to your Obsidian vault path")


@cli.command()
def main() -> None:
    """Create properties.yml from every tier fragment; a no-op if it already exists."""
    if _PROPERTIES_FILE.exists():
        info("properties.yml already exists — leaving it untouched (delete or rename it to regenerate)")
        _sync_gitignore_tracking(_detect_repo_remote())
        return

    _PROPERTIES_FILE.write_text(_build_initial_content())
    info("Created properties.yml")

    repo_local = _detect_repo_local()
    repo_remote = _detect_repo_remote()

    lines = _PROPERTIES_FILE.read_text().splitlines(keepends=True)
    _replace_scalar(lines, "repo", "local", repo_local)
    if repo_remote:
        _replace_scalar(lines, "repo", "remote", repo_remote)
    has_screenshots = _has_section(lines, "screenshots")
    if has_screenshots:
        _replace_scalar(lines, "screenshots", "location", f"{repo_local}/screenshots")
    if _has_section(lines, "icloud"):
        _prompt_icloud_enabled(lines)
    _PROPERTIES_FILE.write_text("".join(lines))
    _sync_gitignore_tracking(repo_remote)

    success(f"properties.yml: repo.local = {repo_local}")
    if repo_remote:
        success(f"properties.yml: repo.remote = {repo_remote}")
    else:
        info("No git remote 'origin' found — repo.remote left unchanged")
    if has_screenshots:
        success(f"properties.yml: screenshots.location = {repo_local}/screenshots")


if __name__ == "__main__":
    main()
