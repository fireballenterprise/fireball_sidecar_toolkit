# modules/backlog
Track bugs / features / tasks as **GitHub Issues**, one tracker per family repo, driven by `gh`.
No local state. Reachable as `/backlog` (+ the `/add_bug`, `/add_feature`, `/add_task` aliases)
and `invoke backlog.*`.

| file | what |
|---|---|
| `route.py` | `/backlog <sub> ...` argument dispatch (dispatch only) |
| `add.py` | `backlog.add` — open an issue (native Type + label) |
| `list.py` | `backlog.list` — list a repo's issues (defaults to this repo) |
| `view.py` | `backlog.view` — show one issue |
| `start.py` | `backlog.start` — show + self-assign an issue, print the repo's ship rules |
| `comment.py` | `backlog.comment` — add a comment |
| `close.py` | `backlog.close` — close, optionally noting the PR / sha that fixed it |
| `common.py` | repo resolution (`resolve_repo`), `gh` wrappers, issue creation, secret scrub, image upload |

## Classification
Each issue gets both the org-native GitHub **issue Type** (`Bug` / `Feature` / `Task`) and a
matching **label** (`bug` / `enhancement` / `task`). A repo whose org has no issue types is filed
with the label only (a warning is printed).

## Repo targeting
`--repo` takes a fuzzy token resolved against `properties.yml` `repos:` — exact name, unique name
substring, or best word overlap against the repo's `purpose`. Ambiguous → the CLI prints the
candidates and exits so the skill can ask. `list` defaults to the current repo; every other verb
needs `--repo` (issues live on a sibling).

## Images
GitHub has no issue-attachment API. The **skill** transcribes a pasted screenshot into the issue
text. For a real on-disk file, `--images "a.png b.png"` uploads each to a per-repo `issue-assets`
pseudo-release and embeds the stable URL.
