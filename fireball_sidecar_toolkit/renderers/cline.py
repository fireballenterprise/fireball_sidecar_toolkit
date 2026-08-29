"""Render ``.clinerules/workflows/*.md`` for Cline.

Cline workflows are body-only (no frontmatter). Cline cannot run an inline ``!`...``` line, so each
one is rewritten into an explicit "Run this terminal command:" fenced block wrapping the same
command. All other body prose is kept as-is.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..catalog import ContentBundle
from ._common import clean_dir, write_doc

_EXEC_LINE = re.compile(r"^!`([^`]+)`[ \t]*$", re.MULTILINE)


def _rewrite(body: str) -> str:
    return _EXEC_LINE.sub(lambda m: f"Run this terminal command:\n\n```\n{m.group(1).strip()}\n```", body)


def render(bundle: ContentBundle, repo_root: Path) -> list[Path]:
    out_dir = repo_root / ".clinerules" / "workflows"
    written = [write_doc(out_dir / f"{c.slug}.md", _rewrite(c.body)) for c in bundle.commands]
    clean_dir(out_dir, written)
    return written
