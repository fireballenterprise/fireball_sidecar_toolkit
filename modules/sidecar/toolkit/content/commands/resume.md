---
name: resume
description: Draft, revise, and render Levon's resume via the local Reactive Resume service
argument-hint: create [--slug value] | update [--slug value] | sync [--file path] | setup | clean
agent: agent
---

!`uv run --no-sync python -m modules.employment.route "$ARGUMENTS"`

If $ARGUMENTS starts with "create" or "update", the command copies a template/latest-draft JSON
file to a new dated path in `docs/resume/raw/` and prints it. Read both source files it names in
full — `topics/employment/docs/history/work_history.md` (raw career material) and
`topics/employment/docs/resume/resume_guidelines.md` (the filtering strategy: what to omit, job
targeting, positioning) — then edit the target JSON file **in place** with real content (`basics`,
`summary`, `sections` — see the Reactive Resume schema already present in the file). Leave
`metadata` (template/design/layout) untouched unless asked to change the look.

If $ARGUMENTS starts with "update", also read the "Base on" file the command printed and revise it
rather than starting from scratch — carry forward anything still accurate, and apply any new
guidance from `resume_guidelines.md` or new content from `work_history.md` added since that base
file was written.

After editing the JSON, run the `sync` command the tool printed
(`uv run --no-sync python -m modules.employment.resume --action=sync --file=<path>`) to push the
content into the local rendering service and produce the PDF at `docs/resume/`.

Keep the resume itself short and scannable per `resume_guidelines.md`'s Format Strategy — do not
pad it with a verbose keyword list disguised as bullets. Keep AI/ATS keyword coverage in the
dedicated Skills section only.

`setup`/`clean` manage the local Docker-based rendering service (Reactive Resume) — `setup` brings
it up (idempotent) and reports whether an API key is configured; `clean` stops it without deleting
data. `create`/`update`/`sync` auto-start the service if it isn't already running, so `setup` is
optional day-to-day.
