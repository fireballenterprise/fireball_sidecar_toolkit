"""Rendering the canonical bundle into every provider view."""

from __future__ import annotations

from pathlib import Path

import pytest

from fireball_sidecar_toolkit.catalog import packaged_content_root
from fireball_sidecar_toolkit.render import render_repo
from fireball_sidecar_toolkit.renderers import GENERATED_HEADER

pytestmark = pytest.mark.sidecar_toolkit


def _mini_content(root: Path) -> Path:
    """A tiny canonical tree: 3 commands (uv / aws / no-exec), 2 instructions, 1 skill."""
    content = root / "content"
    (content / "commands").mkdir(parents=True)
    (content / "instructions").mkdir(parents=True)
    (content / "skills" / "repos").mkdir(parents=True)

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
    (content / "skills" / "repos" / "SKILL.md").write_text(
        "---\nname: repos\ndescription: Repo map skill\nhints:\n  - the repos\n---\n\n"
        "# Repos Trigger\n\nUse this file as source of truth: `.github/prompts/repos.prompt.md`\n"
    )
    return content


def test_every_renderer_produces_output(tmp_path):
    result = render_repo(tmp_path, canonical_root=packaged_content_root())
    produced = {p.relative_to(tmp_path).parts[0] for p in result.written}
    assert {".github", ".claude", ".clinerules", ".opencode", ".sidecar", "AGENTS.md", "CLAUDE.md"} <= produced
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".claude" / "commands" / "fix.md").exists()


def test_generated_header_on_every_markdown_file(tmp_path):
    for path in render_repo(tmp_path, canonical_root=packaged_content_root()).written:
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


def test_cline_rewrites_exec_lines(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    fix = (tmp_path / ".clinerules" / "workflows" / "fix.md").read_text()
    assert "!`" not in fix
    assert "Run this terminal command:" in fix
    assert "uv run --no-sync invoke fix" in fix


def test_agents_index_lists_every_instruction(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    agents = (tmp_path / "AGENTS.md").read_text()
    assert "`.github/instructions/git.instructions.md`" in agents
    assert "`.github/instructions/python.instructions.md`" in agents
    assert "**Git & PR**" in agents  # label derived from the H1


def test_sidecar_files_point_at_materialized_paths(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    cmd = (tmp_path / ".sidecar" / "commands" / "fix.md").read_text()
    assert "Use this file as source of truth: .github/prompts/fix.prompt.md" in cmd
    inst = (tmp_path / ".sidecar" / "instructions" / "python.md").read_text()
    assert 'applyTo: "**/*.py"' in inst
    assert "Use this file as source of truth: .github/instructions/python.instructions.md" in inst


def test_skill_dirs_copied_to_claude_and_github(tmp_path):
    render_repo(tmp_path, canonical_root=_mini_content(tmp_path))
    for dest in (".claude/skills/repos/SKILL.md", ".github/skills/repos/SKILL.md"):
        text = (tmp_path / dest).read_text()
        assert "# Repos Trigger" in text
        assert GENERATED_HEADER in text


def test_local_overlay_overrides_and_adds(tmp_path):
    canonical = _mini_content(tmp_path)
    local = tmp_path / "_local"
    (local / "commands").mkdir(parents=True)
    (local / "commands" / "fix.md").write_text(
        "---\nname: fix\ndescription: LOCAL fix\nargument-hint: none\nagent: agent\n---\n\n!`./setup.sh`\n"
    )
    (local / "commands" / "deploy.md").write_text(
        "---\nname: deploy\ndescription: repo-only deploy\nargument-hint: none\nagent: agent\n---\n\n!`uv run --no-sync invoke deploy`\n"
    )
    render_repo(tmp_path, canonical_root=canonical)

    fix = (tmp_path / ".claude" / "commands" / "fix.md").read_text()
    assert "LOCAL fix" in fix
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
