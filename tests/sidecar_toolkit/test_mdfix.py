"""Markdown normalisation — blank-after-header and stray-divider removal."""

from __future__ import annotations

import pytest

from fireball_sidecar_toolkit.mdfix import MarkdownStyleError, check_tree, fix_tree, normalize

pytestmark = pytest.mark.sidecar_toolkit


def test_removes_blank_line_after_header():
    src = "# Title\n\nIntro.\n\n## Section\n\n- a\n- b\n"
    assert normalize(src) == "# Title\nIntro.\n\n## Section\n- a\n- b\n"


def test_collapses_multiple_blank_lines_after_header():
    assert normalize("## S\n\n\n\ntext\n") == "## S\ntext\n"


def test_blank_line_before_header_is_kept():
    src = "para\n\n## Next\ntext\n"
    assert normalize(src) == src


def test_header_inside_code_fence_is_untouched():
    src = "## Real\ntext\n\n```md\n## Fake\n\nstill fenced\n```\n"
    assert normalize(src) == src


def test_frontmatter_is_preserved():
    src = '---\napplyTo: "**"\n---\n# Title\n\nbody\n'
    assert normalize(src, instruction_file=True) == '---\napplyTo: "**"\n---\n# Title\nbody\n'


def test_divider_removed_only_for_instruction_files():
    src = "# T\ntext\n\n---\n\n## Next\nmore\n"
    assert normalize(src, instruction_file=True) == "# T\ntext\n\n## Next\nmore\n"
    assert normalize(src, instruction_file=False) == src  # thematic break kept elsewhere


def test_divider_inside_fence_is_kept_for_instruction_files():
    src = "# T\ntext\n\n```markdown\n---\napplyTo: x\n---\n```\n"
    assert normalize(src, instruction_file=True) == src


def test_normalize_is_idempotent():
    once = normalize("## S\n\nx\n\n---\n\n## T\ny\n", instruction_file=True)
    assert normalize(once, instruction_file=True) == once


def test_fix_tree_and_check_tree(tmp_path):
    (tmp_path / "docs").mkdir()
    good = tmp_path / "docs" / "good.md"
    good.write_text("## S\nfine\n")
    bad = tmp_path / "docs" / "bad.md"
    bad.write_text("## S\n\nneeds fixing\n")
    (tmp_path / "instructions").mkdir()
    inst = tmp_path / "instructions" / "x.md"
    inst.write_text("# X\ntext\n\n---\n\n## Y\nmore\n")

    with pytest.raises(MarkdownStyleError, match="bad.md"):
        check_tree(tmp_path)

    changed = fix_tree(tmp_path, write=True)
    assert set(p.name for p in changed) == {"bad.md", "x.md"}
    assert good.read_text() == "## S\nfine\n"
    assert "\n\nneeds fixing" not in bad.read_text()
    assert "---" not in inst.read_text()
    check_tree(tmp_path)  # clean now


def test_exclude_skips_a_tree(tmp_path):
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics" / "gen.md").write_text("## S\n\ngenerated, do not touch\n")
    (tmp_path / "kept.md").write_text("## S\n\nfix me\n")

    changed = fix_tree(tmp_path, write=True, exclude=("topics",))
    assert [p.name for p in changed] == ["kept.md"]
    assert (tmp_path / "topics" / "gen.md").read_text() == "## S\n\ngenerated, do not touch\n"
    check_tree(tmp_path, exclude=("topics",))  # passes despite the untouched topics file
