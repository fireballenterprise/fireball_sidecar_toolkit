"""Parse canonical content trees (and a consuming repo's ``_local/``) into structured records.

Two content roots feed every renderer:

* the packaged canonical tree — ``content/`` in this repo, shipped as package data
* an optional per-repo overlay — ``_local/`` in the consuming repo

``load_bundle()`` merges them (``_local/`` wins on a name collision) and returns a
:class:`ContentBundle` the renderers consume. Nothing here writes files or knows about any
specific AI tool — that is the renderers' job.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_EXEC_RE = re.compile(r"^!`([^`]+)`", re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return ``(frontmatter_dict, body)`` for a markdown file with optional ``---`` frontmatter."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                fm = {}
            return (fm if isinstance(fm, dict) else {}), parts[2].strip()
    return {}, text.strip()


@dataclass(frozen=True)
class Command:
    """One canonical slash-command spec (``content/commands/<slug>.md``)."""

    slug: str
    description: str
    argument_hint: str
    body: str
    source: Path

    @property
    def exec_line(self) -> str:
        """The ``!`...``` execution line from the body, or ``""`` if the command has none."""
        match = _EXEC_RE.search(self.body)
        return match.group(1).strip() if match else ""

    @classmethod
    def from_file(cls, path: Path) -> Command:
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        return cls(
            slug=path.stem,
            description=str(fm.get("description", "")),
            argument_hint=str(fm.get("argument-hint", "")),
            body=body,
            source=path,
        )


@dataclass(frozen=True)
class Instruction:
    """One canonical agent-rule file (``content/instructions/<slug>.md``)."""

    slug: str
    description: str
    apply_to: str
    body: str
    source: Path

    @classmethod
    def from_file(cls, path: Path) -> Instruction:
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        return cls(
            slug=path.stem,
            description=str(fm.get("description", "")),
            apply_to=str(fm.get("applyTo", "")),
            body=body,
            source=path,
        )


@dataclass(frozen=True)
class Skill:
    """One canonical skill directory (``content/skills/<name>/``)."""

    name: str
    root: Path


@dataclass(frozen=True)
class ContentBundle:
    """Everything the renderers need: merged canonical + ``_local/`` content."""

    commands: list[Command] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    local_slugs: frozenset[str] = frozenset()

    def is_local(self, slug: str) -> bool:
        """True when ``slug`` came from the consuming repo's ``_local/`` overlay."""
        return slug in self.local_slugs


def _collect(root: Path, subdir: str, suffix: str = ".md") -> list[Path]:
    target = root / subdir
    if not target.is_dir():
        return []
    return sorted(p for p in target.glob(f"*{suffix}") if p.is_file())


def packaged_content_root() -> Path:
    """Absolute path to the ``content/`` tree bundled with the installed package."""
    return (Path(__file__).resolve().parents[2] / "content").resolve()


def load_bundle(*, canonical_root: Path | None = None, local_root: Path | None = None) -> ContentBundle:
    """Merge the canonical tree with an optional ``_local/`` overlay into a :class:`ContentBundle`.

    Args:
        canonical_root: ``content/`` root. Defaults to the packaged tree.
        local_root: consuming repo's ``_local/`` root. Optional.
    """
    canonical_root = (canonical_root or packaged_content_root()).resolve()

    commands: dict[str, Command] = {}
    instructions: dict[str, Instruction] = {}
    skills: dict[str, Skill] = {}
    local_slugs: set[str] = set()

    for path in _collect(canonical_root, "commands"):
        commands[path.stem] = Command.from_file(path)
    for path in _collect(canonical_root, "instructions"):
        instructions[path.stem] = Instruction.from_file(path)
    for skill_dir in sorted((canonical_root / "skills").glob("*/")) if (canonical_root / "skills").is_dir() else []:
        skills[skill_dir.name] = Skill(name=skill_dir.name, root=skill_dir)

    if local_root and local_root.is_dir():
        for path in _collect(local_root, "commands"):
            commands[path.stem] = Command.from_file(path)
            local_slugs.add(path.stem)
        for path in _collect(local_root, "instructions"):
            instructions[path.stem] = Instruction.from_file(path)
            local_slugs.add(path.stem)
        skills_root = local_root / "skills"
        for skill_dir in sorted(skills_root.glob("*/")) if skills_root.is_dir() else []:
            skills[skill_dir.name] = Skill(name=skill_dir.name, root=skill_dir)
            local_slugs.add(skill_dir.name)

    return ContentBundle(
        commands=[commands[k] for k in sorted(commands)],
        instructions=[instructions[k] for k in sorted(instructions)],
        skills=[skills[k] for k in sorted(skills)],
        local_slugs=frozenset(local_slugs),
    )
