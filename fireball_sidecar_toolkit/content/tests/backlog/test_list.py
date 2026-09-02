"""modules.toolkit.backlog.list — single-repo and `--all` family aggregation."""

import json
import subprocess
from pathlib import Path

import pytest
from modules.toolkit.backlog import list as backlog_list
from modules.toolkit.setup.properties import FamilyRepo

pytestmark = pytest.mark.backlog


def _repo(name, *, org="fireballenterprise"):
    return FamilyRepo(
        org=org,
        name=name,
        path=Path("/nonexistent") / name,
        is_self=False,
        exists=False,
        default_branch="main",
        parent=None,
        status="active",
        visibility="private",
        ai=False,
        use_ci=False,
        pull_request=False,
        purpose="",
    )


_FAMILY = [_repo("fireball_sidecar_vscode"), _repo("fireball_sidecar_toolkit"), _repo("fireball_orchestrator")]

#: fuzzy `--repo` token → the repo it resolves to.
_RESOLVE = {
    "toolkit": "fireball_sidecar_toolkit",
    "orchestrator": "fireball_orchestrator",
    "": "fireball_sidecar_toolkit",
}

#: `org/name` → the fake `gh issue list` stdout for that repo (one TSV row per issue).
_ROWS = {
    "fireballenterprise/fireball_sidecar_vscode": "12\tblank chat panel\tSidecar VSCode\topen\n",
    "fireballenterprise/fireball_sidecar_toolkit": "52\tlist --all\tSidecar Toolkit\topen\n",
    "fireballenterprise/fireball_orchestrator": "",
}
_JSON_ROWS = {
    "fireballenterprise/fireball_sidecar_vscode": '[{"number":12,"title":"blank chat panel"}]',
    "fireballenterprise/fireball_sidecar_toolkit": '[{"number":52,"title":"list --all"}]',
    "fireballenterprise/fireball_orchestrator": "",
}


@pytest.fixture(autouse=True)
def _stub(monkeypatch):
    monkeypatch.setattr(backlog_list, "get_family_repos", lambda **_kw: list(_FAMILY))
    monkeypatch.setattr(backlog_list, "resolve_repo_or_current", lambda token: _repo(_RESOLVE[token]))

    def fake_gh(args, *, repo=None, check=True):
        table = _JSON_ROWS if "--json" in args else _ROWS
        return subprocess.CompletedProcess(args, 0, stdout=table.get(repo, ""), stderr="")

    monkeypatch.setattr(backlog_list, "gh", fake_gh)


def test_single_repo_header_and_rows(capsys):
    backlog_list.main(repo="toolkit")
    out = capsys.readouterr().out
    assert "Open issues in fireballenterprise/fireball_sidecar_toolkit:" in out
    assert "52\tlist --all" in out


def test_single_repo_empty_state(capsys):
    backlog_list.main(repo="orchestrator")
    assert "No open issues in fireballenterprise/fireball_orchestrator." in capsys.readouterr().out


def test_all_groups_by_repo_and_collapses_empty(capsys):
    backlog_list.main(all_repos=True)
    out = capsys.readouterr().out
    assert "fireballenterprise/fireball_sidecar_vscode — 1 open" in out
    assert "  12\tblank chat panel\tSidecar VSCode" in out
    assert "fireballenterprise/fireball_orchestrator — none" in out
    assert "2 open issue(s) across 3 repos." in out


def test_all_json_tags_each_row_with_repo(capsys):
    backlog_list.main(all_repos=True, as_json=True)
    payload = json.loads(capsys.readouterr().out)
    assert {row["repo"] for row in payload} == {
        "fireballenterprise/fireball_sidecar_vscode",
        "fireballenterprise/fireball_sidecar_toolkit",
    }
    assert {row["number"] for row in payload} == {12, 52}


def test_all_and_repo_are_mutually_exclusive():
    with pytest.raises(SystemExit):
        backlog_list.main(all_repos=True, repo="toolkit")


def test_scope_requires_all():
    with pytest.raises(SystemExit):
        backlog_list.main(scope="ai")


def test_scope_must_be_known():
    with pytest.raises(SystemExit):
        backlog_list.main(all_repos=True, scope="bogus")
