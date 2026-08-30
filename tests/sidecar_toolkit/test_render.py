"""Rendering the canonical bundle into every provider view."""

from __future__ import annotations

from pathlib import Path

import pytest

from fireball_sidecar_toolkit.catalog import packaged_ai_root
from fireball_sidecar_toolkit.render import render_repo
from fireball_sidecar_toolkit.renderers import GENERATED_HEADER

pytestmark = pytest.mark.sidecar_toolkit


def _mini_content(root: Path) -> Path:
    """A tiny canonical tree: 3 commands (uv / aws / no-exec), 2 instructions, 1 skill."""
    content = root / "content"
    (content / "commands").mkdir(parents=True)
    (content / "instructions").mkdir(parents=True)
    (content / "skills").mkdir(parents=True)

    (content / "commands" / "fix.md").write_text(
        "---\nname: fix\ndescription: Auto-fix lint\nargument-hint: none\nagent: agent\n---\n\n"
        "!`uv run --no-sync invoke fix`\n"
    )
    (content / "commands" / "bedrock.md").write_text(
        "---\nname: bedrock\ndescription: Check models\nargument-hint: none\nagent: agent\n---\n\n"
        '!`AWS_PROFILE=fireballenterprise uv run --no-sync python -m modules.bedrock.route "$ARGUMENTS"`\n'
    )
    (content / "commands" / "repos.md").write_text(
        "---\nname: repos\ndescription: Show the repo map\nargument-hint: none\nagent: agent\n---\n\n"
        "Read `.github/instructions/repos.instructions.md` and follow it.\n"
    )
    (content / "instructions" / "git.md").write_text(
        '---\ndescription: "Branch + PR rules"\n---\n# Git & PR Instructions\n\nBranch naming rules.\n'
    )
    (content / "instructions" / "python.md").write_text(
        '---\ndescription: "Python rules"\napplyTo: "**/*.py"\n---\n# Python\n\nType hints everywhere.\n'
    )
    (content / "skills" / "repos.md").write_text(
        "---\nname: repos\ndescription: Repo map skill\nhints:\n  - the repos\n---\n\n"
        "# Repos Trigger\n\nUse this file as source of truth: `.ai/toolkit/commands/repos.md`\n"
    )
    return content


def test_every_renderer_produces_output(tmp_path):
    result = render_repo(tmp_path, canonical_root=packaged_ai_root())
    produced = {p.relative_to(tmp_path).parts[0] for p in result.written}
    assert {".github", ".claude", ".clinerules", ".sidecar", "AGENTS.md", "CLAUDE.md"} <= produced
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".claude" / "commands" / "fix.md").exists()


def test_generated_header_on_every_markdown_file(tmp_path):
    for path in render_repo(tmp_path, canonical_root=packaged_ai_root()).written:
        if path.suffix == ".md":
            assert GENERATED_HEADER in path.read_text(encoding="utf-8"), path


def test_claude_allowed_tools_are_derived(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    fix = (tmp_path / ".claude" / "commands" / "fix.md").read_text()
    assert "allowed-tools: Bash(uv run --no-sync *)" in fix

    bedrock = (tmp_path / ".claude" / "commands" / "bedrock.md").read_text()
    assert "Bash(AWS_PROFILE=fireballenterprise uv run --no-sync *)" in bedrock
    assert "Bash(uv run --no-sync *)" in bedrock

    repos = (tmp_path / ".claude" / "commands" / "repos.md").read_text()
    assert "allowed-tools" not in repos  # prose-only command


def test_cline_is_a_pointer_stub(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    fix = (tmp_path / ".clinerules" / "workflows" / "fix.md").read_text()
    assert "!`" not in fix
    assert "Run this terminal command:" not in fix
    assert "Source of truth: `.ai/toolkit/commands/fix.md`" in fix


def test_agents_index_lists_every_instruction(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    agents = (tmp_path / "AGENTS.md").read_text()
    assert "`.ai/toolkit/instructions/git.md`" in agents
    assert "`.ai/toolkit/instructions/python.md`" in agents
    assert "**Git & PR**" in agents  # label derived from the H1


def test_sidecar_files_point_at_canonical_ai_paths(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    cmd = (tmp_path / ".sidecar" / "commands" / "fix.md").read_text()
    assert "Source of truth: `.ai/toolkit/commands/fix.md`" in cmd
    inst = (tmp_path / ".sidecar" / "instructions" / "python.md").read_text()
    assert 'applyTo: "**/*.py"' in inst
    assert "Source of truth: `.ai/toolkit/instructions/python.md`" in inst


def test_skill_stubs_written_for_claude_and_github(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    for dest in (".claude/skills/repos/SKILL.md", ".github/skills/repos/SKILL.md"):
        text = (tmp_path / dest).read_text()
        assert "# Repos Trigger" not in text  # body is NOT inlined
        assert "Source of truth: `.ai/toolkit/skills/repos.md`" in text
        assert GENERATED_HEADER in text


def test_no_canonical_body_is_inlined(tmp_path):
    """Every generated file is a stub — a sentence from a canonical body never leaks through."""
    result = render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    for path in result.written:
        if path.suffix == ".md":
            assert "Type hints everywhere." not in path.read_text(encoding="utf-8"), path
    inst = (tmp_path / ".github" / "instructions" / "python.instructions.md").read_text()
    assert "Source of truth: `.ai/toolkit/instructions/python.md`" in inst
    assert 'applyTo: "**/*.py"' in inst


def test_local_overlay_overrides_and_adds(tmp_path):
    canonical = _mini_content(tmp_path)
    local = tmp_path / ".ai" / tmp_path.name  # the local layer dir is named after the repo folder
    (local / "commands").mkdir(parents=True)
    (local / "commands" / "fix.md").write_text(
        "---\nname: fix\ndescription: LOCAL fix\nargument-hint: none\nagent: agent\n---\n\n!`./setup.sh`\n"
    )
    (local / "commands" / "deploy.md").write_text(
        "---\nname: deploy\ndescription: repo-only deploy\nargument-hint: none\nagent: agent\n---\n\n!`uv run --no-sync invoke deploy`\n"
    )
    render_repo(tmp_path, canonical_root=canonical)

    fix = (tmp_path / ".claude" / "commands" / "fix.md").read_text()
    assert "description: LOCAL fix" in fix  # provider frontmatter still reflects the overlay
    assert f"Source of truth: `.ai/{tmp_path.name}/commands/fix.md`" in fix  # pointer → the local layer
    assert "allowed-tools: Bash(./setup.sh)" in fix
    assert (tmp_path / ".claude" / "commands" / "deploy.md").exists()
    assert (tmp_path / ".github" / "prompts" / "deploy.prompt.md").exists()


def test_dropped_slug_is_cleaned_on_rerender(tmp_path):
    canonical = _mini_content(tmp_path)
    render_repo(tmp_path, canonical_root=canonical)
    assert (tmp_path / ".claude" / "commands" / "bedrock.md").exists()

    (canonical / "commands" / "bedrock.md").unlink()
    render_repo(tmp_path, canonical_root=canonical)
    assert not (tmp_path / ".claude" / "commands" / "bedrock.md").exists()
    assert not (tmp_path / ".github" / "prompts" / "bedrock.prompt.md").exists()
    assert (tmp_path / ".claude" / "commands" / "fix.md").exists()
