"""Tests for topic listing behavior."""

import io
import sys
from contextlib import redirect_stdout

import pytest
import yaml
from modules.toolkit.topic import list as topic_list
from modules.toolkit.topic import route as topic_route

pytestmark = pytest.mark.topic


def test_topic_route_list_all_passes_flag(monkeypatch):
    """Route should forward the all-topics flag to the topic list module."""
    calls: dict[str, object] = {}

    def fake_run(module: str, args: list[str]) -> int:
        calls["module"] = module
        calls["args"] = args
        return 0

    monkeypatch.setattr(topic_route, "_run", fake_run)
    monkeypatch.setattr(sys, "argv", ["topic.route", "list all"])

    result = topic_route.main()

    assert result == 0
    assert calls == {"module": "modules.toolkit.topic.list", "args": ["--all"]}


def test_topic_list_defaults_to_active_only(temp_repo, monkeypatch):
    """Default topic list should show only the active topic and the all-topics hint."""
    topics_yaml = temp_repo / "topics" / "topics_list.yml"
    topics_yaml.write_text(yaml.safe_dump({"topics_layout": {"test": {"example": {}}}}, sort_keys=False))

    monkeypatch.setattr(topic_list, "get_repo_local", lambda: temp_repo)
    monkeypatch.setattr(topic_list, "read_active_topic", lambda _repo: "test/example")

    monkeypatch.setattr(sys, "argv", ["topic.list"])

    output = io.StringIO()
    with redirect_stdout(output):
        topic_list.main()

    rendered = output.getvalue()
    assert "⭐ Active Topic: test/example" in rendered
    assert "Use /topic list all" in rendered
    assert "📚 Available Topics" not in rendered


def test_topic_list_all_shows_full_tree(temp_repo, monkeypatch):
    """The all-topics option should render the full topic tree."""
    topics_yaml = temp_repo / "topics" / "topics_list.yml"
    topics_yaml.write_text(yaml.safe_dump({"topics_layout": {"test": {"example": {}}}}, sort_keys=False))

    monkeypatch.setattr(topic_list, "get_repo_local", lambda: temp_repo)
    monkeypatch.setattr(topic_list, "read_active_topic", lambda _repo: "test/example")

    monkeypatch.setattr(sys, "argv", ["topic.list", "--all"])

    output = io.StringIO()
    with redirect_stdout(output):
        topic_list.main()

    rendered = output.getvalue()
    assert "📚 Available Topics" in rendered
    assert "⭐ Active Topic: test/example" in rendered
    assert "test/" in rendered
