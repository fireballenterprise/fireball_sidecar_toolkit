"""download / check / sync against a throwaway git repo."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from fireball_sidecar_toolkit import sync
from fireball_sidecar_toolkit.check import DriftError, check
from fireball_sidecar_toolkit.download import DirtySharedError, download

pytestmark = pytest.mark.sidecar_toolkit


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t.t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("x\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "init")
    return tmp_path


def test_download_clobbers_shared_and_renders(repo: Path):
    result = download(repo)
    assert result.by_count > 20
    assert (repo / ".ai" / "toolkit" / "commands").is_dir()
    assert (repo / ".ai" / "toolkit" / "instructions").is_dir()
    assert (repo / "AGENTS.md").exists()
    assert (repo / ".claude" / "commands").is_dir()


def test_download_clobbers_the_shared_python_and_scripts(repo: Path):
    download(repo)
    assert (repo / "modules" / "toolkit" / "setup" / "properties.py").is_file()
    assert (repo / "tasks" / "toolkit" / "common" / "main.py").is_file()
    assert (repo / "tests" / "toolkit").is_dir()
    setup = repo / "setup.sh"
    assert setup.is_file() and setup.stat().st_mode & 0o111  # executable
    assert (repo / "setup.ps1").is_file()


def test_check_flags_a_tampered_shared_module(repo: Path):
    download(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "generated")
    (repo / "modules" / "toolkit" / "setup" / "properties.py").write_text("tampered\n")
    with pytest.raises(DriftError, match="modules/toolkit/setup/properties.py"):
        check(repo)


def test_check_passes_immediately_after_download(repo: Path):
    download(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "generated")
    check(repo)  # no raise


def test_check_raises_when_a_generated_file_is_edited(repo: Path):
    download(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "generated")
    (repo / "AGENTS.md").write_text("hand-edited\n")
    with pytest.raises(DriftError, match="AGENTS.md"):
        check(repo)


def test_check_raises_when_shared_is_missing(repo: Path):
    with pytest.raises(DriftError, match=".ai/toolkit"):
        check(repo)


def test_download_allows_untracked_shared(repo: Path):
    download(repo)  # creates an untracked _shared/
    download(repo)  # a second run before committing must not trip the dirty guard


def test_download_refuses_dirty_shared(repo: Path):
    download(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "generated")
    (repo / ".ai" / "toolkit" / "commands" / "fix.md").write_text("tampered\n")
    with pytest.raises(DirtySharedError):
        download(repo)
    download(repo, force=True)  # force overrides


def test_sync_inspect_reports_clean_then_dirty(repo: Path):
    download(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "generated")
    assert sync.inspect(repo).dirty is False

    (repo / ".ai" / "toolkit" / "commands" / "fix.md").write_text("tampered\n")
    plan = sync.inspect(repo)
    assert plan.dirty is True
    assert "fix.md" in plan.shared_diff
