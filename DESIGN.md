# ai_devkit — Design

Single source of truth for Levon's shared AI-agent tooling. Canonical slash commands, agent
instructions, and skills live here as tool-neutral markdown; a generator renders them into every
AI tool's native format inside each consuming repo.

Full project plan and history: `ai_vault` repo →
`topics/help/engineering/plans/consolidate_ai_toolkit.md`.

## Repository layout
```
content/
  instructions/*.md   canonical agent rules (frontmatter: description, applyTo)
  commands/*.md       canonical slash-command specs (frontmatter: name, description,
                      argument-hint; body carries the !`...` exec line)
  skills/<name>/SKILL.md
modules/
  devkit/
    cli.py            `devkit` console entrypoint (argparse -> download/upload/sync/check)
    content.py        parse content/ (and a repo's _local/) into Command / Instruction / Skill
    download.py       clobber _shared/ from the installed package, then render
    upload.py         diff _shared/ vs canonical -> open a PR against ai_devkit
    sync.py           check _shared/ for edits -> offer upload -> download -> render
    render.py         orchestrate all renderers over (content + _local/)
    renderers/
      agents.py       -> AGENTS.md + CLAUDE.md (thin pointer)
      claude.py       -> .claude/commands/ + .claude/skills/
      cline.py        -> .clinerules/workflows/
      copilot.py      -> .github/copilot-instructions.md + .github/instructions/
      opencode.py     -> .opencode/command/
      prompts.py      -> .github/prompts/  (kept for GitHub.com prompt-file UI)
      sidecar.py      -> .sidecar/  (ideally a no-op; Sidecar reads canonical files directly)
  setup/, versioning/, common/   inherited from template_python
tasks/
  devkit/             invoke wrappers: devkit.download, devkit.upload, devkit.sync, devkit.check
```

## Distribution
`ai_devkit` is pip-installable by GitHub URL (not on PyPI). Each consuming repo adds:
```toml
[dependency-groups]
dev = ["ai-devkit @ git+https://github.com/levonbecker/ai_devkit@1"]
```
Pinned to the floating major tag `1`; `uv.lock` captures the exact commit. The wheel bundles
`content/` as package data, so `devkit download` clobbers `_shared/` straight from the installed
package — no network, no Copier, no submodule.

## Consuming-repo contract
```
_shared/    clobbered copy of ai_devkit content/ — NEVER hand-edited
_local/     this repo's own instructions/ commands/ skills/ — never synced, never overwritten
<generated> .claude/ .github/{prompts,instructions,copilot-instructions.md} .clinerules/
            .opencode/ .sidecar/ AGENTS.md CLAUDE.md — NEVER hand-edited
```
- `devkit download` — clobber `_shared/` to canonical, render every provider view (with `_local/`
  layered on top), run the drift check.
- `devkit upload` — diff `_shared/` vs canonical, open a PR against `ai_devkit` with the changes
  (only `_shared/` files; refuses `_local/` and generated output).
- `devkit sync` — check `_shared/` for uncommitted edits → surface them and ask whether to upload
  first → then download → render. This is what `/devkit_sync` and the skill call; the AI does the
  asking.
- `devkit check` — read-only drift gate for `invoke fix` / `invoke test` and CI.

## Open design questions
1. **Shared vs local content split.** The initial port copied *all* of ai_vault's
   `.github/instructions/` and `.github/prompts/`. Truly shared (belongs here): `git`, `logic`,
   `review`, `style`, `layout`, `python`, `tasks`, `tests`, `docs`, `skills`, `prompts`,
   `versioning` instructions; `push`, `pull`, `rebase`, `fix`, `ss`, `pr*`, `ship-it`, `squash`,
   `setup`, `test`, `update`, `upgrade`, `template` commands. ai_vault-local (should move to
   `_local/`): `topics`, `travel`, `personal`, `repos` instructions; `chat`, `topic`, `repos`,
   `financials`, `resume`, `update_card_limit` commands. Decide before first real `download`.
2. **`_local/` merge semantics** — additive-only, or per-file override of a `_shared/` file?
3. **Circular dependency** — `ai_devkit` is scaffolded from `template_python`; once
   `template_python` also consumes `ai_devkit`, keep `ai_devkit` free of the `ai-devkit` dep
   (it *is* the source) and render its own provider views from its own `content/`.
4. **Exec-line rewriting** — canonical command bodies use
   `!`uv run --no-sync python -m modules.<x>.route`. Consuming repos may need a different module
   path prefix; the renderer may need a token the repo substitutes.
