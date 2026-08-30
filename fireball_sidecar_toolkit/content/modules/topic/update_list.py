"""Manage the git-tracked index of all topic paths in topics/topics_list.yml.

The file has two keys:

- `topics:` — the sorted list of every registered topic path.
- `topic_meta:` — an optional map of `path -> {description, instructions}` for topics
  that carry a description or a list of applicable `.github/instructions/` slugs. Only
  topics that need it appear here; the rest have no entry. `/topic update` reads this
  to regenerate each `AGENTS.md` (see `templates.render_agents_md`).
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..setup.properties import get_repo_root

LOGGER = logging.getLogger(__name__)

_TOPICS_LIST_FILE = "topics_list.yml"


class _IndentedDumper(yaml.SafeDumper):
    """Indent block-sequence items under their key (PyYAML's default doesn't, yamllint wants it to)."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def _topics_list_path() -> Path:
    return get_repo_root() / "topics" / _TOPICS_LIST_FILE


def _load() -> dict:
    path = _topics_list_path()
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _write(topics: list[str], meta: dict[str, dict]) -> None:
    payload: dict[str, object] = {"topics": sorted(topics)}
    pruned = {path: value for path, value in sorted(meta.items()) if value and path in topics}
    if pruned:
        payload["topic_meta"] = pruned
    _topics_list_path().write_text(yaml.dump(payload, Dumper=_IndentedDumper, sort_keys=False))


def list_topics() -> list[str]:
    """Return all registered topic paths, sorted."""
    return sorted(_load().get("topics", []))


def topic_meta(topic_path: str) -> dict:
    """Return `{description, instructions}` for `topic_path`, or `{}` if it has no metadata."""
    return _load().get("topic_meta", {}).get(topic_path, {}) or {}


def topic_exists(topic_path: str) -> bool:
    """Return whether `topic_path` is registered and its directory exists."""
    return topic_path in list_topics() and (get_repo_root() / "topics" / topic_path).is_dir()


def add_topic(
    topic_path: str,
    description: str | None = None,
    instructions: list[str] | None = None,
    body: str | None = None,
) -> None:
    """Register `topic_path` in topics_list.yml, keeping any existing `topic_meta` intact.

    A supplied `description`/`instructions`/`body` is stored under `topic_meta:`; passing
    none for an already-registered topic leaves its metadata untouched.
    """
    data = _load()
    topics = data.get("topics", [])
    meta = data.get("topic_meta", {}) or {}

    if topic_path not in topics:
        topics.append(topic_path)

    entry = dict(meta.get(topic_path, {}) or {})
    if description is not None:
        entry["description"] = description
    if instructions is not None:
        entry["instructions"] = list(instructions)
    if body is not None:
        entry["body"] = body
    if entry:
        meta[topic_path] = entry

    _write(topics, meta)
