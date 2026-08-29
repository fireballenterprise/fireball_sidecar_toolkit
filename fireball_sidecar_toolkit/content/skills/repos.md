---
name: repos
description: Use for showing this vault's related-repos map (org/repo list + template lineage) from properties.yml, pulling every repo in the family up to date, or applying a change across related repos. Equivalent to /repos. Also triggered by the phrases "related repos", "the repos", "other repos", or "all of the repos".
hints:
  - related repos
  - the repos
  - other repos
  - all of the repos
  - all the repos
  - pull all repos
  - pull all the repos
  - pull the repos
  - pull every repo
---

# Repos Trigger

Use this file as source of truth: `.ai/shared/commands/repos.md`

When the user says "related repos", "the repos", "other repos", "all of the repos", "pull all repos", or otherwise
asks about this vault's repo family — even without running `/repos` — read
`.ai/shared/instructions/repos.md` in full and follow it. It covers both the
`repos`/`lineage` map and the two-phase (apply, then checkpoint, then ship) Cross-Repo Change
Workflow.
