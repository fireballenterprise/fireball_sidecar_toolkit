# modules/toolkit/repo/
Repository-level git and PR operations. Thin CLI wrappers — logic lives in these modules, reached
via `/repo`, the dedicated aliases, or `inv repo.*`.

## Commands
| Command | Module | Purpose |
|---|---|---|
| `/repo push` (`/push`) | `push.py` | pull → detect changes → commit with timestamp → push to remote → rsync content to the iCloud Obsidian folder. Runs `modules.toolkit.screenshots.clean --no-confirm` first. |
| `/repo pull` (`/pull`) | `pull.py` | stash → `pull --rebase` → restore stash; also pulls the iCloud folder |
| `/rebase` | `rebase.py` | rebase the current branch onto the remote default branch (optional squash first) |
| `/squash` | `squash.py` | anchored squash of all commits to the root commit, optional force push |
| `/pr` `/pr-notes` | `pr_diff.py`, `pr_notes.py`, `pr_create.py` | draft PR notes (Summary + Changes) for the current branch and open the PR via `gh` |
| `/ship-it` | `pr_push.py` + `pr_create.py` | push the branch and open the PR in one step |
| `/pr-cleanup` | `pr_cleanup.py` | after merge: switch to the default branch, pull, delete the merged local branch |

`route.py` dispatches the `/repo` subcommands. Branch naming and PR format: see
`.github/instructions/git.instructions.md`.

## iCloud Sync
`push.py` / `pull.py` rsync repo **content** (topics, screenshots, docs) to the iCloud Obsidian
vault when `icloud.enabled: true` in `properties.yml` — excluding `.git`, `.claude`, and other
hidden files so the mobile vault stays small (~700KB). It's off by default.

## Notes
- Every module has a `main()` entry point and uses `modules/toolkit/setup/properties.py` for path resolution
- The screenshot workflow moved to `modules/toolkit/screenshots/`
