"""Render the repo-root entrypoints.

* ``AGENTS.md`` — the tool-neutral **index**: a short preamble, one bullet per instruction linking
  to its canonical ``ai/shared/`` (or ``ai/local/``) file, and the source-of-truth note.
* ``CLAUDE.md`` — a fixed short pointer to ``AGENTS.md``.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import write_doc

_PREAMBLE = (
    "This repo's rules for any AI coding tool are authored once under `ai/shared/` (synced from "
    "`fireball_sidecar_toolkit`) and `ai/local/` (this repo's own). Every `.github/`, `.claude/`, "
    "`.clinerules/`, and `.sidecar/` file is a generated pointer back to them. Read the relevant "
    "canonical file before making changes:"
)

_SOURCE_OF_TRUTH = (
    "**Source of truth: `ai/shared/` and `ai/local/`** — all rules, slash commands, and skills "
    "live there as tool-neutral markdown. Never hand-edit a generated provider file "
    "(`.github/`, `.claude/`, `.clinerules/`, `.sidecar/`, `AGENTS.md`, `CLAUDE.md`); edit the "
    "`ai/` source and run `invoke sidecar.toolkit.download`."
)

_CLAUDE_MD = f"""# Claude Code Instructions

See `AGENTS.md` for all instructions — it links to every canonical file under `ai/shared/` and
`ai/local/`, the source of truth for this repo's rules, slash commands, and skills.

{_SOURCE_OF_TRUTH}
"""


def _canonical(bundle: ContentBundle, slug: str) -> str:
    layer = "local" if bundle.is_local(slug) else "shared"
    return f"ai/{layer}/instructions/{slug}.md"


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    bullets = "\n".join(f"- **{i.label}**: `{_canonical(bundle, i.slug)}`" for i in bundle.instructions)
    agents_body = f"# Agent Instructions\n\n{_PREAMBLE}\n\n{bullets}\n\n{_SOURCE_OF_TRUTH}"
    return [
        write_doc(repo_root / "AGENTS.md", agents_body),
        write_doc(repo_root / "CLAUDE.md", _CLAUDE_MD),
    ]
