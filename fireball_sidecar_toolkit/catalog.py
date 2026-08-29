"""Parse the canonical content tree (and a consuming repo's ``_local/``) into structured records.

Two content roots feed every renderer:

* ``_shared`` — the packaged canonical tree (``content/`` in this repo, shipped as package data)
* ``_local`` — an optional per-repo overlay in the consuming repo

``load_bundle()`` merges them (``_local`` wins on a slug collision) and returns a
:class:`ContentBundle` the renderers consume. Nothing here writes files or knows about any
specific AI tool — that is the renderers' job.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Content layers, lowest-priority first. A slug defined in a later layer overrides the earlier one.
# `_shared` is the packaged canonical tree; `_local` is the consuming repo's overlay.
LAYERS = ("_shared", "_local")

_EXEC_RE = re.compile(r"^!`([^`]+)`", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _as_list(value: object) -> list[str]:
    """Normalise a frontmatter scalar/list into a list of stripped strings."""
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


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
    agent: str = "agent"
    allowed_tools: tuple[str, ...] = ()

    @property
    def exec_lines(self) -> list[str]:
        """Every ``!`...``` execution line in the body, in order."""
        return [match.group(1).strip() for match in _EXEC_RE.finditer(self.body)]

    @property
    def exec_line(self) -> str:
        """The first ``!`...``` execution line from the body, or ``""`` if the command has none."""
        lines = self.exec_lines
        return lines[0] if lines else ""

    @classmethod
    def from_file(cls, path: Path) -> Command:
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        return cls(
            slug=path.stem,
            description=str(fm.get("description", "")),
            argument_hint=str(fm.get("argument-hint", "")),
            body=body,
            source=path,
            agent=str(fm.get("agent", "agent")),
            allowed_tools=tuple(_as_list(fm.get("allowed-tools"))),
        )


@dataclass(frozen=True)
class Instruction:
    """One canonical agent-rule file (``content/instructions/<slug>.md``)."""

    slug: str
    description: str
    apply_to: str
    body: str
    source: Path
    label: str = ""

    @classmethod
    def from_file(cls, path: Path) -> Instruction:
        fm, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        return cls(
            slug=path.stem,
            description=str(fm.get("description", "")),
            apply_to=str(fm.get("applyTo", "")),
            body=body,
            source=path,
            label=str(fm.get("label", "")) or _derive_label(path.stem, body),
        )


def _derive_label(slug: str, body: str) -> str:
    """A human label for the AGENTS.md / copilot index: frontmatter ``label`` → body H1 → slug."""
    match = _H1_RE.search(body)
    if match:
        return re.sub(r"\s+(Instructions|Workflow)$", "", match.group(1).strip())
    return slug.replace("_", " ").replace("-", " ").title()


@dataclass(frozen=True)
class Skill:
    """One canonical skill directory (``content/skills/<name>/``)."""

    name: str
    root: Path

    @property
    def skill_file(self) -> Path:
        return self.root / "SKILL.md"

    def read(self) -> tuple[dict, str]:
        """``(frontmatter, body)`` of this skill's ``SKILL.md``."""
        return _split_frontmatter(self.skill_file.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ContentBundle:
    """Everything the renderers need: the merged ``_shared`` + ``_vault`` + ``_local`` content."""

    commands: list[Command] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    # slug -> layer name it was resolved from (e.g. "_shared", "_vault", "_local")
    origin: dict[str, str] = field(default_factory=dict)

    def layer_of(self, slug: str) -> str | None:
        """Which layer a slug was resolved from, or ``None`` if unknown."""
        return self.origin.get(slug)

    def is_local(self, slug: str) -> bool:
        """True when ``slug`` was resolved from the consuming repo's ``_local/`` overlay."""
        return self.origin.get(slug) == "_local"


def _collect(root: Path, subdir: str, suffix: str = ".md") -> list[Path]:
    target = root / subdir
    if not target.is_dir():
        return []
    return sorted(p for p in target.glob(f"*{suffix}") if p.is_file())


def packaged_content_root() -> Path:
    """Absolute path to the ``content/`` tree bundled inside this package."""
    return (Path(__file__).resolve().parent / "content").resolve()


def _skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(p for p in skills_root.glob("*/") if p.is_dir())


def load_bundle(*, canonical_root: Path | None = None, local_root: Path | None = None) -> ContentBundle:
    """Merge the content layers into a :class:`ContentBundle`.

    Layers apply lowest-priority first: ``canonical_root`` (``_shared``, defaults to the packaged
    tree) → ``local_root`` (``_local``). A slug present in a later layer replaces the earlier one;
    :attr:`ContentBundle.origin` records which layer won.

    Args:
        canonical_root: the toolkit ``content/`` root. Defaults to the packaged tree.
        local_root: consuming repo's ``_local/`` root. Optional.
    """
    layers: list[tuple[str, Path]] = [("_shared", (canonical_root or packaged_content_root()).resolve())]
    if local_root is not None:
        layers.append(("_local", local_root.resolve()))

    commands: dict[str, Command] = {}
    instructions: dict[str, Instruction] = {}
    skills: dict[str, Skill] = {}
    origin: dict[str, str] = {}

    for layer_name, root in layers:
        if not root.is_dir():
            continue
        for path in _collect(root, "commands"):
            commands[path.stem] = Command.from_file(path)
            origin[path.stem] = layer_name
        for path in _collect(root, "instructions"):
            instructions[path.stem] = Instruction.from_file(path)
            origin[path.stem] = layer_name
        for skill_dir in _skill_dirs(root):
            skills[skill_dir.name] = Skill(name=skill_dir.name, root=skill_dir)
            origin[skill_dir.name] = layer_name

    return ContentBundle(
        commands=[commands[k] for k in sorted(commands)],
        instructions=[instructions[k] for k in sorted(instructions)],
        skills=[skills[k] for k in sorted(skills)],
        origin=origin,
    )
