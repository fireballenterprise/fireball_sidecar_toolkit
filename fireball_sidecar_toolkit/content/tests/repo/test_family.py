"""modules.toolkit.repo.family + get_family_repos — resolution, ordering, singleton fallback."""

import pytest
from modules.toolkit.repo import family
from modules.toolkit.setup import properties

pytestmark = pytest.mark.repo


def _clone(base, name):
    (base / name / ".git").mkdir(parents=True)
    return base / name


@pytest.fixture
def family_props(tmp_path, monkeypatch):
    org = tmp_path / "org"
    for name in ("template_python", "template_ai_python", "ai_vault"):
        _clone(org, name)
    props = {
        "repos": {
            "acme": ["template_python", "template_ai_python", "ai_vault", "ghost_repo"],
            "lineage": {"template_python": [{"template_ai_python": ["ai_vault"]}]},
        },
        "repos_local": {"acme": str(org)},
        "repo": {"local": str(org / "ai_vault")},
    }
    monkeypatch.setattr(properties, "get_properties", lambda: props)
    monkeypatch.setattr(properties, "get_repo_local", lambda: org / "ai_vault")
    return org


def test_orders_root_to_leaf_and_drops_self_and_missing(family_props):
    assert [r.name for r in properties.get_family_repos()] == ["template_python", "template_ai_python"]


def test_include_self_appends_self_last_and_flags_it(family_props):
    repos = properties.get_family_repos(include_self=True)
    assert [r.name for r in repos] == ["template_python", "template_ai_python", "ai_vault"]
    assert repos[-1].is_self and not repos[0].is_self


def test_no_repos_key_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(properties, "get_properties", lambda: {"repo": {"local": str(tmp_path)}})
    monkeypatch.setattr(properties, "get_repo_local", lambda: tmp_path)
    assert properties.get_family_repos() == []


def test_run_family_singleton_fallback(monkeypatch, capsys):
    monkeypatch.setattr(family, "get_family_repos", lambda *, include_self: [])
    dispatched = []
    monkeypatch.setattr(family, "_dispatch_single", lambda verb: dispatched.append(verb) or 0)
    assert family.run_family("pull") == 0
    assert dispatched == ["pull"]
    assert "no repos: family map" in capsys.readouterr().out


def test_print_map_without_family(monkeypatch, capsys):
    monkeypatch.setattr(family, "get_properties", lambda: {"repos": {}})
    assert family.print_map() == 0
    assert "no related-repo family" in capsys.readouterr().out
