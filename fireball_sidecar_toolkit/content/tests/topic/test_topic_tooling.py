"""Topic scaffolding + AGENTS.md generation — modules/topic/."""

from __future__ import annotations

import pytest
import yaml
from modules.toolkit.topic import init, templates, update, update_list

pytestmark = pytest.mark.topic


@pytest.fixture
def topics_root(tmp_path, monkeypatch):
    (tmp_path / "topics").mkdir()
    for module in (update_list, init, update):
        monkeypatch.setattr(module, "get_repo_root", lambda: tmp_path, raising=False)
    return tmp_path


def _list_yml(root) -> dict:
    return yaml.safe_load((root / "topics" / "topics_list.yml").read_text())


class TestRenderAgentsMd:
    def test_includes_description_and_instruction_links(self):
        out = templates.render_agents_md("sidecar_vscode", "The extension topic.", ["sidecar", "sidecar_vscode"])
        assert "# Agent Instructions — sidecar_vscode" in out
        assert "The extension topic." in out
        assert "## Instructions" in out
        assert "[`sidecar`](../../.github/instructions/sidecar.instructions.md)" in out
        assert "[`sidecar_vscode`](../../.github/instructions/sidecar_vscode.instructions.md)" in out

    def test_nested_topic_gets_deeper_relative_path(self):
        out = templates.render_agents_md("a/b", instructions=["sidecar"])
        assert "(../../../.github/instructions/sidecar.instructions.md)" in out

    def test_no_instructions_section_when_none_given(self):
        out = templates.render_agents_md("plain")
        assert "## Instructions" not in out
        assert "- Chats: `chats/`" in out


class TestTopicMetaPersistence:
    def test_add_topic_stores_and_reads_back_meta(self, topics_root):
        update_list.add_topic("sidecar_chat", "The web app.", ["sidecar", "sidecar_chat"])
        assert update_list.list_topics() == ["sidecar_chat"]
        assert update_list.topic_meta("sidecar_chat") == {
            "description": "The web app.",
            "instructions": ["sidecar", "sidecar_chat"],
        }

    def test_add_topic_without_meta_leaves_existing_meta_intact(self, topics_root):
        update_list.add_topic("sidecar", "Umbrella.", ["sidecar"])
        update_list.add_topic("sidecar")  # re-register, no meta args
        assert update_list.topic_meta("sidecar")["description"] == "Umbrella."

    def test_plain_topic_has_no_meta_entry(self, topics_root):
        update_list.add_topic("amazon")
        assert update_list.topic_meta("amazon") == {}
        assert "topic_meta" not in _list_yml(topics_root)

    def test_write_is_yaml_round_trippable(self, topics_root):
        update_list.add_topic("sidecar", "Umbrella.", ["sidecar"])
        update_list.add_topic("amazon")
        data = _list_yml(topics_root)
        assert data["topics"] == ["amazon", "sidecar"]
        assert data["topic_meta"] == {"sidecar": {"description": "Umbrella.", "instructions": ["sidecar"]}}


class TestScaffoldAndUpdate:
    def test_scaffold_writes_agents_md_with_instruction_links(self, topics_root):
        topic_dir = topics_root / "topics" / "sidecar_llm"
        topic_dir.mkdir()
        init.scaffold(topic_dir, "sidecar_llm", "Local LLM.", ["sidecar", "sidecar_llm"])
        agents = (topic_dir / "AGENTS.md").read_text()
        assert "Local LLM." in agents
        assert "[`sidecar_llm`](../../.github/instructions/sidecar_llm.instructions.md)" in agents

    def test_update_regenerates_from_stored_meta(self, topics_root, monkeypatch):
        topic_dir = topics_root / "topics" / "sidecar_vscode"
        topic_dir.mkdir()
        init.scaffold(topic_dir, "sidecar_vscode", "Extension.", ["sidecar", "sidecar_vscode"])
        (topic_dir / "AGENTS.md").write_text("# clobbered by a human\n")

        monkeypatch.setattr(update.topic_active, "get_active_topic", lambda: "sidecar_vscode")
        update.main(dry_run=False, current_only=True)

        agents = (topic_dir / "AGENTS.md").read_text()
        assert "Extension." in agents
        assert "[`sidecar_vscode`](../../.github/instructions/sidecar_vscode.instructions.md)" in agents

    def test_split_instructions_parses_csv(self):
        assert init.split_instructions("sidecar, sidecar_chat ,sidecar_vscode") == [
            "sidecar",
            "sidecar_chat",
            "sidecar_vscode",
        ]
        assert init.split_instructions(None) is None
        assert init.split_instructions("") is None
