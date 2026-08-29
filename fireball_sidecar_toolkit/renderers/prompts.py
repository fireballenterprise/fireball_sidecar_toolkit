"""Render ``.github/prompts/*.prompt.md`` — the GitHub.com prompt-file picker view.

This is the in-repo *materialisation* of each canonical command: full frontmatter
(``name``/``description``/``argument-hint``/``agent``) and the canonical body verbatim, inline
``!`...``` exec line included. Every generated pointer file (``.claude/``, ``.sidecar/``,
``.clinerules/``) refers back to the file this renderer writes.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, write_doc


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    out_dir = repo_root / ".github" / "prompts"
    written = [
        write_doc(
            out_dir / f"{command.slug}.prompt.md",
            command.body,
            frontmatter={
                "name": command.slug,
                "description": command.description,
                "argument-hint": command.argument_hint,
                "agent": command.agent,
            },
        )
        for command in bundle.commands
    ]
    clean_dir(out_dir, written)
    return written
