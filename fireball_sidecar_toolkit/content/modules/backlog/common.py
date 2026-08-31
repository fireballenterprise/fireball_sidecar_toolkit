"""Shared plumbing for every `backlog` verb: family-repo resolution, `gh` wrappers, issue
creation (native Type + label), the secret scrub, and image upload.

`common` is the only backlog module the verb files import from — no verb imports another verb.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import NoReturn

from ..common import cli
from ..common.utils import error, warning
from ..setup.properties import FamilyRepo, find_current_repo, get_family_repos

#: `--type` vocabulary → the org-native GitHub issue Type (title-cased) set on the issue.
ISSUE_TYPES = {"bug": "Bug", "feature": "Feature", "task": "Task"}

#: `--type` vocabulary → the label written alongside the native Type. `bug` / `enhancement` are
#: GitHub defaults on every repo; `task` is upserted on first use (see `ensure_label`).
TYPE_LABELS = {"bug": "bug", "feature": "enhancement", "task": "task"}

#: Dedicated pseudo-release that issue image attachments are uploaded to — GitHub has no
#: issue-attachment API. One per repo, `--prerelease`, created on first `--images` use.
ISSUE_ASSET_TAG = "issue-assets"

_LABEL_SPECS = {"task": ("A specific piece of work", "BFD4F2")}

_REDACTION = "\u2039redacted\u203a"

#: High-confidence secret shapes scrubbed from every issue body / comment before it is sent.
#: Best-effort defence in depth — the skill does the primary, context-aware pass.
_SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
    re.compile(r"\barn:aws:[a-z0-9-]*:[a-z0-9-]*:\d{12}:\S+"),
    re.compile(r"(?im)^\s*(?:aws_)?(?:secret_)?access_key(?:_id)?\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(?:bearer|authorization|api[_-]?key|token|secret|password|passwd)\b\s*[:=]\s*\S+"),
    re.compile(r"\b[a-z][\w+.-]*://[^\s:/@]+:[^\s:/@]+@\S+"),
)


def _fail_resolution(token: str, candidates: list[FamilyRepo], active: list[FamilyRepo]) -> NoReturn:
    """Print the plausible matches (or the whole active list) and exit — the skill re-asks."""
    if candidates:
        cli.echo(f"'{token}' matches several repos — pass an exact name:")
        for repo in candidates:
            cli.echo(f"  {repo.name} — {repo.purpose}")
        error("ambiguous --repo")
    cli.echo("Known repos:")
    for repo in active:
        cli.echo(f"  {repo.name} — {repo.purpose}")
    error(f"no repo matches '{token}'")


def _last_line(text: str) -> str:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def create_issue(repo_nwo: str, *, title: str, body: str, issue_type: str, labels: list[str]) -> str:
    """Open an issue with the org-native Type set. Falls back to label-only when the repo's org
    has no issue types (e.g. personal repos). Returns the new issue URL."""
    ensure_label(repo_nwo, TYPE_LABELS[issue_type])
    base = ["issue", "create", "--title", title, "--body", body, "--label", ",".join(labels)]
    typed = gh([*base, "--type", ISSUE_TYPES[issue_type]], repo=repo_nwo, check=False)
    if typed.returncode == 0:
        return _last_line(typed.stdout)
    if "issue type" in typed.stderr.lower() or "not have issue types" in typed.stderr.lower():
        warning(f"{repo_nwo}: org has no issue types — filed with the '{TYPE_LABELS[issue_type]}' label only")
        return _last_line(gh(base, repo=repo_nwo).stdout)
    error(f"`gh issue create` failed: {typed.stderr.strip() or 'no output'}")


def ensure_label(repo_nwo: str, name: str) -> None:
    """Upsert a non-default label (`task`) so `gh issue create --label` never fails on it."""
    spec = _LABEL_SPECS.get(name)
    if spec is None:
        return
    description, color = spec
    gh(
        ["label", "create", name, "--force", "--description", description, "--color", color],
        repo=repo_nwo,
        check=False,
    )


def gh(args: list[str], *, repo: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a `gh` command (optionally `--repo org/name`). Exits via `error()` on a non-zero exit
    unless `check=False`, in which case the `CompletedProcess` is handed back for inspection."""
    command = ["gh", *args]
    if repo:
        command += ["--repo", repo]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        error(f"`gh {' '.join(args)}` failed: {result.stderr.strip() or result.stdout.strip() or 'no output'}")
    return result


def issue_json(repo_nwo: str, number: int, fields: str) -> dict:
    """`gh issue view --json <fields>` parsed to a dict."""
    return json.loads(gh(["issue", "view", str(number), "--json", fields], repo=repo_nwo).stdout)


def nwo(repo: FamilyRepo) -> str:
    """`org/name` for `gh --repo`."""
    return f"{repo.org}/{repo.name}"


def resolve_repo(token: str) -> FamilyRepo:
    """Fuzzy-match `token` to one family repo. Ladder: exact name / `org/name` → unique name
    substring → best word overlap against name + purpose. Retired repos are reachable only by
    exact name. Ambiguous or unknown → print candidates and exit (the skill then asks)."""
    token = token.strip()
    repos = get_family_repos(include_self=True, include_retired=True, include_missing=True)
    for repo in repos:
        if token == repo.name or token.lower() == nwo(repo).lower():
            return repo

    active = [repo for repo in repos if repo.status == "active"]
    lowered = token.lower()
    substring = [repo for repo in active if lowered in repo.name.lower()]
    if len(substring) == 1:
        return substring[0]

    wanted = _words(token)
    scored = sorted(
        ((len(wanted & _words(f"{repo.name} {repo.purpose}")), repo) for repo in (substring or active)),
        key=lambda pair: pair[0],
        reverse=True,
    )
    best = [repo for score, repo in scored if score and score == scored[0][0]]
    if len(best) == 1:
        return best[0]
    _fail_resolution(token, best or substring, active)


def resolve_repo_or_current(token: str) -> FamilyRepo:
    """`resolve_repo(token)` when given, else this repo's own row (for `list` with no `--repo`)."""
    if token:
        return resolve_repo(token)
    current = find_current_repo()
    if current is None:
        error("this repo isn't in properties.yml's repos: map — pass --repo")
    return current


def scrub(text: str) -> str:
    """Redact high-confidence secrets from an issue body / comment before sending it to GitHub."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(_REDACTION, text)
    return text


def upload_issue_asset(repo_nwo: str, path: Path) -> str:
    """Upload `path` to the repo's `issue-assets` pseudo-release (created on first use) and return
    the stable download URL to embed in an issue body."""
    if gh(["release", "view", ISSUE_ASSET_TAG], repo=repo_nwo, check=False).returncode != 0:
        gh(
            [
                "release",
                "create",
                ISSUE_ASSET_TAG,
                "--prerelease",
                "--title",
                "Issue attachments",
                "--notes",
                "Images referenced from issues. Not a real release.",
            ],
            repo=repo_nwo,
        )
    gh(["release", "upload", ISSUE_ASSET_TAG, str(path), "--clobber"], repo=repo_nwo)
    return f"https://github.com/{repo_nwo}/releases/download/{ISSUE_ASSET_TAG}/{path.name}"


def with_images(repo_nwo: str, body: str, images: str) -> str:
    """Append an `![name](url)` line for each space-separated path in `images`, uploading as it
    goes. Exits if a path is missing."""
    for raw in images.split():
        path = Path(raw).expanduser()
        if not path.is_file():
            error(f"image not found: {raw}")
        body += f"\n\n![{path.stem}]({upload_issue_asset(repo_nwo, path)})"
    return body
