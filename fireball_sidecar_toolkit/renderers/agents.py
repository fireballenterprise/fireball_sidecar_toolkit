"""Render the repo-root entrypoints.

* ``AGENTS.md`` — the tool-neutral **index**: a short preamble, one bullet per instruction linking
  to its materialised ``.github/instructions/`` file, and the source-of-truth note. It is an index,
  not a concatenation — the full text lives in the linked files.
* ``CLAUDE.md`` — a fixed short pointer to ``AGENTS.md``.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import write_doc

_PREAMBLE = (
    "This repo's rules for any AI coding tool live in `.github/instructions/`. Read the relevant "
    "file before making changes:"
)

_SOURCE_OF_TRUTH = (
    "**Source of truth: `.github/instructions/` and `.github/prompts/`** — all rules and slash "
    "commands live there. Never duplicate rules into this file or any tool-specific entrypoint — "
    "update `.github/instructions/` only."
)

_CLAUDE_MD = f"""# Claude Code Instructions

See `AGENTS.md` for all instructions — it links to every file in `.github/instructions/`, the
source of truth for this repo's rules and slash commands.

{_SOURCE_OF_TRUTH}
"""


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    bullets = "\n".join(
        f"- **{i.label}**: `.github/instructions/{i.slug}.instructions.md`" for i in bundle.instructions
    )
    agents_body = f"# Agent Instructions\n\n{_PREAMBLE}\n\n{bullets}\n\n{_SOURCE_OF_TRUTH}"
    return [
        write_doc(repo_root / "AGENTS.md", agents_body),
        write_doc(repo_root / "CLAUDE.md", _CLAUDE_MD),
    ]
