---
name: backlog
description: Track bugs / features / tasks as GitHub Issues on any repo in the family — file, list, view, work, comment, close. Use for "file a bug in X", "list the issues for X", "work on issue N", "fix all the open bugs in X".
argument-hint: add bug|feature|task --repo <name> --title "..." | list [--repo <name>] | start --repo <name> --number N | close --repo <name> --number N --pr M
agent: agent
---

!`uv run --no-sync python -m modules.toolkit.backlog.route "$ARGUMENTS"`

Issues are the tracker — no local bug/backlog markdown. `--repo` is a fuzzy token (name, unique
substring, or a word from the repo's `purpose`); an ambiguous token makes the CLI print
candidates — ask the user which, don't guess. `list` defaults to the current repo; every other
verb needs `--repo`.

**Type vs. labels** — two axes, don't conflate them:

- `--type bug|feature|task` sets the org-native GitHub **issue Type**. That's the whole
  bug/feature/task classification — there is no `bug` label.
- **Labels** carry *area* and *nature*. Every issue automatically gets its repo's area
  (`Sidecar VSCode`, `Sidecar Toolkit`, …). Add finer ones with `--area` when you know them: the
  affected **module, component, topic, or concept** (`--area backlog`, `--area router`,
  `--area topics`, `--area verbs`), or "where it surfaces" when that differs from the fix's repo.
  Add `--label` for *nature*: `Regression`, `Usage Failure`, `UI`, `Hallucination`,
  `Performance`, `Docs`. Any label that doesn't exist is created automatically. **Propose the
  `--area` / `--label` values at the confirm step** — don't file without showing them.

## Recognition — what the user says maps to what to run
| user says | do |
|---|---|
| "file/log/track a bug in sidecar vscode: X", "feature request for the toolkit: Y", "add a task for chat: Z" | resolve the repo; craft a clean title + a body in the **issue format** below (ask if the report is thin). If an image was pasted, **read it and transcribe the relevant content into the body** — error text as fenced quotes, UI state as prose; note it came from a screenshot. Work out `--area` (affected module/component/topic, from the "Where it likely lives" analysis) and any `--label` nature; **confirm title + Type + area + labels with the user**, then `backlog.add --repo <t> --type <bug\|feature\|task> --title "..." --body "..." [--area <m>] [--label <nature>]` |
| "list / show the issues \| open bugs \| backlog for X", "what's left \| still open in X" | `backlog.list --repo <t>` (`--type bug` for bugs, `--label <area>` to scope to a module/topic; `--state open` by default) |
| "work on / pick up / start / tackle issue N in X", "fix this bug" (issue in context) | `backlog.start --repo <t> --number N` then open the **target repo's** clone, branch per its ship rules (the command prints them), implement, run its `invoke fix && invoke test`, `/push` or `/pr`, then `backlog.close --repo <t> --number N --pr <n>` (or `--sha <sha>` for direct-push repos) |
| "fix all the open bugs \| issues in X", "knock out the backlog for X" | `backlog.list --repo <t> --state open --json`, **show the list, confirm the batch**, work one at a time each on its own branch/commit, `backlog.close` each, report a summary; stop and surface any that need a decision |
| "close issue N in X, fixed by PR M" | `backlog.close --repo <t> --number N --pr M` |
| "add a note to issue N", "comment on N" | `backlog.comment --repo <t> --number N --body "..."` |

## Issue body format
Written for an AI to pick up and work — err verbose, but lead with a human summary:

```
**Summary:** 1-2 lines a human skims to know what this is.

## What happens
<full repro: the report verbatim where it helps; transcribed screenshot content; repro steps if known>

## Where it likely lives
<repo/file/function pointers, suspected cause — only if known; omit rather than guess>

## Done when
<concrete acceptance: the behaviour that proves it's fixed; the smoke check to run>
```

Feature / task variant: `**Summary:**` then `## Request` then `## Why / details` then `## Done when`.

## Guardrails
- **Scrub secrets / PII before every `add` and `comment`** — API keys, tokens, passwords, `.env`
  values, AWS account IDs + ARNs, Cognito IDs, connection strings, creds-in-URLs, customer emails.
  The CLI runs a backstop pass; you do the primary, context-aware one. Matters most for
  transcribed screenshots and pasted logs — transcribe the *error*, not the secret. If redacting
  would gut the repro, ask the user how to proceed rather than posting it.
- **Confirm any multi-issue batch** before starting; one issue per branch/commit.
- **Honour each repo's `properties.yml` ship rules** — `backlog.start` prints them. `pull_request:
  true` means feature branch + PR (assigned to the user). `pull_request: false` means commit
  straight to the default branch, no PR. Never open a PR or push to a shared branch without
  naming the repo and branch first.
- Never merge a PR yourself.
