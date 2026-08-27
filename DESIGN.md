# fireball_sidecar_toolkit — Design

Single source of truth for the shared AI-agent tooling. Canonical slash commands, agent
instructions, and skills live here as tool-neutral markdown; a generator renders them into every
AI tool's native format inside each consuming repo.

Full project plan and history: `ai_vault` repo →
`topics/help/engineering/plans/consolidate_ai_toolkit.md`.

## Naming
| thing | value |
|-------|-------|
| GitHub repo | `fireballenterprise/fireball_sidecar_toolkit` |
| PyPI / dist name | `fireball-sidecar-toolkit` (unique, brand-scoped) |
| import package | `modules.sidecar.toolkit` |
| invoke namespace | `sidecar.toolkit.{download,upload,sync,check,release}` |
| console script | `sidecar-toolkit` (for the `uvx`, no-dependency path) |
| slash commands | `/toolkit_sync`, `/toolkit_download`, `/toolkit_upload` (naming TBC) |

## Repository layout
```
modules/
  sidecar/
    toolkit/
      content/
        instructions/*.md   canonical agent rules (frontmatter: description, applyTo)
        commands/*.md        canonical slash-command specs (name, description, argument-hint;
                             body carries the !`...` exec line)
        skills/<name>/SKILL.md
      cli.py            `sidecar-toolkit` console entrypoint
      content.py        parse content/ (+ a repo's _local/) -> ContentBundle
      render.py         run every renderer over the bundle
      renderers/        one per target: agents, claude, cline, copilot, opencode, prompts, sidecar
      download.py       clobber _shared/ from the installed package, then render
      upload.py         diff _shared/ vs canonical -> PR against this repo
      sync.py           check _shared/ -> offer upload -> download -> render
      check.py          read-only drift gate
      release.py        promote development -> main, cut a tag
  setup/, versioning/, common/   inherited from template_python
tasks/
  sidecar/toolkit/     invoke wrappers
```

## Branch model & channels
Both `main` and `development` are **PR-required** (ruleset "PR to Main + Development": `deletion` +
`non_fast_forward` blocked, `pull_request` required, 0 approvals; bypass actors = org admins and
the `fireball-actions-bot` App, `always`). `development` is the default branch.

* **`development`** — integration branch; feature PRs merge here. Every merge runs `version.yml`
  → `invoke ver.project_bump_build` bumps `VERSION` (`X.Y.Z-NNN`). Dev channel:
  `fireball-sidecar-toolkit @ git+https://github.com/fireballenterprise/fireball_sidecar_toolkit@development`
* **`main`** — stable; only updated by `release.yml` promoting `development` (via
  `sidecar.toolkit.release`). Default channel: pin the floating major tag `@1` (always the latest
  `1.x.x` on `main`; no `v` prefix, starts at `1.0.0`).
* `VERSION` (`X.Y.Z[-NNN]`) is the release-process truth; `pyproject.toml`'s `version` stays at
  the target `X.Y.Z` and is not auto-synced (git-installed, so it rarely matters).
* **Tagged releases** cut from `main` by `.github/workflows/release.yml` (GitHub release now;
  PyPI later — workflows not usable until after 2026-09-01). Once on PyPI: `development` publishes
  dev releases (`X.Y.Z.devN`, install with `--prerelease=allow`), `main` tags publish finals.

### release.yml (dispatch-triggered; `sidecar.toolkit.release` = `gh workflow run release.yml`)
Adapted from `fireball_sidecar_landing/release.yml` + `workflows_shopify/publish_release.yml`.
Auth: `main` is protected (require PR); the org-wide **`fireball-actions-bot`** App
(`vars.BOT_APP_ID` + `secrets.BOT_PRIVATE_KEY`, via `actions/create-github-app-token@v3`) is the
bypass actor for the promote push. `development` stays open, so its bumps use plain `GITHUB_TOKEN`.
Jobs:
1. **version** — `invoke ver.project_bump_release` drops the `-NNN` build suffix; commit
   `chore: release X.Y.Z [skip ci]`; push `development`.
2. **promote** — `git merge origin/development --no-ff -X theirs` onto `main`; push (bot token).
3. **tag** — `git tag X.Y.Z` + `git tag -f X` (floating major); push both. **No `v` prefix.**
   Guard on `git ls-remote --tags` so re-runs are safe.
4. **publish_release** — `gh release create X.Y.Z --target main --generate-notes`.
5. **pypi** (after 2026-09-01) — PyPI Trusted Publishing / OIDC: `id-token: write` +
   `pypa/gh-action-pypi-publish`, no secret; pending publisher configured on PyPI.

## Distribution
Each consuming repo adds a dev dependency (default = stable):
```toml
[dependency-groups]
dev = ["fireball-sidecar-toolkit @ git+https://github.com/fireballenterprise/fireball_sidecar_toolkit@1"]
```
`uv.lock` captures the exact commit; updates are deliberate
(`uv lock --upgrade-package fireball-sidecar-toolkit`). The wheel bundles `content/` as package
data, so `download` clobbers `_shared/` straight from the install — no network, no Copier, no
submodule. Non-Python / day-job repo:
`uvx --from git+https://github.com/fireballenterprise/fireball_sidecar_toolkit sidecar-toolkit download`.

## Consuming-repo contract
```
_shared/    clobbered copy of the toolkit's content/ — NEVER hand-edited
_local/     this repo's own instructions/ commands/ skills/ — never synced, never overwritten
<generated> .claude/ .github/{prompts,instructions,copilot-instructions.md} .clinerules/
            .opencode/ .sidecar/ AGENTS.md CLAUDE.md — NEVER hand-edited
```
- `sidecar.toolkit.download` — clobber `_shared/` to canonical, render every provider view (with
  `_local/` layered on top), run the drift check.
- `sidecar.toolkit.upload` — diff `_shared/` vs canonical, open a PR against this repo (only
  `_shared/` files; refuses `_local/` and generated output).
- `sidecar.toolkit.sync` — check `_shared/` for uncommitted edits -> surface them and ask whether
  to upload first -> then download -> render. What `/toolkit_sync` and the skill call.
- `sidecar.toolkit.check` — read-only drift gate for `invoke fix` / `invoke test` and CI.
- `sidecar.toolkit.release` — (toolkit repo, and a convenience wrapper elsewhere) promote
  `development` -> `main` and cut a tag.

## Open design questions
1. **Shared vs local content split.** The initial port copied *all* of ai_vault's
   `.github/instructions/` and `.github/prompts/`. See the plan's Shared-vs-Local table for the
   agreed division. ai_vault-specific files move to `_local/` before the first real `download`.
2. **`_local/` merge semantics** — additive-only, or per-file override of a `_shared/` file?
3. **Circular dependency** — this repo is scaffolded from `template_python`; once `template_python`
   also consumes the toolkit, keep the toolkit free of its own dependency (it *is* the source) and
   render its own provider views from its own `content/`.
4. **Exec-line rewriting** — canonical command bodies use
   `!`uv run --no-sync python -m modules.<x>.route`. Consuming repos may need a different module
   path prefix; the renderer may need a token the repo substitutes.
5. **Slash-command names** — `/toolkit_*` vs `/devkit_*` vs `/sidecar_*` (the last collides with
   the Sidecar product name).
6. **Shared release wrapper** — item 3 from the chat: ship `sidecar.toolkit.release` (and
   `.upload`) as part of the toolkit's own shared task set so every repo can
   `sidecar.toolkit.upload && sidecar.toolkit.release` easily.
