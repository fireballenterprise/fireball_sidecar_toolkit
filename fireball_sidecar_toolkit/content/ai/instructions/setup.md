---
description: "Use when setting up a repo for the first time, editing setup.sh / setup.local.sh, or working on modules/setup/ (the properties.yml bootstrap)."
applyTo: "setup.sh,setup.ps1,setup.local.sh,setup.local.ps1,setup_templates/**,modules/setup/**"
---
# Setup
## First-time setup
```sh
./setup.sh          # macOS / Linux
.\setup.ps1         # Windows (PowerShell)
```
Both install `uv` (user-local, no sudo/admin), run the repo-local hook, create `.venv`, `uv sync`,
then hand off to `uv run --no-sync invoke setup.properties` to write `properties.yml`.

## `setup.sh` / `setup.ps1` are clobbered
They come from `fireball_sidecar_toolkit` (`content/scripts/`) — `invoke sidecar.toolkit.download`
overwrites them. **Never edit them.** Anything repo-specific goes in `setup.local.sh` /
`setup.local.ps1` (git-tracked, never clobbered). The base script sources it once and calls two
optional phase functions:
- `setup_local_tools` — after the OS tool install, **before** the venv (install extra tools here:
  Node, esbuild, …)
- `setup_local_post` — **after** `properties.yml` is written (things that read it: `invoke
  aws.cdk.ensure`, …)

```sh
# setup.local.sh — a repo that needs Node + a post-properties step
install_node_fnm() { ... }
setup_local_tools() { install_node_fnm; npm install --global esbuild; }
setup_local_post()  { uv run --no-sync invoke aws.cdk.ensure; }
```
PowerShell: `Setup-Local-Tools` / `Setup-Local-Post` in `setup.local.ps1`.

## `properties.yml` bootstrap (`modules/setup/properties.py`)
- Assembled once, on first run, from `setup_templates/*.yml` at the **repo root** (repo-local — the
  `setup` module is clobbered, so the tier fragments cannot live beside it). One fragment per repo
  in the lineage (`template_python.yml` … `ai_vault.yml`), deep-merged; `repo.local`,
  `repo.remote`, `screenshots.location` stamped with detected values.
- A no-op every run after that — it only ever *creates* the file. To regenerate: delete
  `properties.yml` and re-run.
- Gitignored in `template_*` repos; the ignore line is stripped on first real setup so a scaffolded
  repo commits its `properties.yml`.
