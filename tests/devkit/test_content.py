"""Parsing the canonical content trees and a _local/ overlay."""

import pytest

from modules.devkit.content import load_bundle, packaged_content_root

pytestmark = pytest.mark.devkit


def test_packaged_bundle_parses():
    bundle = load_bundle(canonical_root=packaged_content_root())
    assert bundle.commands, "expected canonical commands"
    assert bundle.instructions, "expected canonical instructions"
    assert all(c.slug for c in bundle.commands)
    assert not bundle.local_slugs


def test_command_exec_line_extracted():
    bundle = load_bundle(canonical_root=packaged_content_root())
    push = next((c for c in bundle.commands if c.slug == "push"), None)
    assert push is not None
    assert push.exec_line.startswith("uv run")


def test_local_overlay_wins_and_is_flagged(tmp_path):
    canonical = tmp_path / "content"
    (canonical / "commands").mkdir(parents=True)
    (canonical / "instructions").mkdir(parents=True)
    (canonical / "commands" / "push.md").write_text("---\ndescription: canonical\n---\nbody\n")

    local = tmp_path / "_local"
    (local / "commands").mkdir(parents=True)
    (local / "commands" / "push.md").write_text("---\ndescription: local override\n---\nlocal body\n")
    (local / "commands" / "mine.md").write_text("---\ndescription: repo-only\n---\nx\n")

    bundle = load_bundle(canonical_root=canonical, local_root=local)
    push = next(c for c in bundle.commands if c.slug == "push")
    assert push.description == "local override"
    assert bundle.is_local("push")
    assert bundle.is_local("mine")
