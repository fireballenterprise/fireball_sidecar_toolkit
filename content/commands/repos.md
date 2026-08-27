---
name: repos
description: Show this vault's related-repos map (org/repo list + template lineage) from properties.yml, pull the whole family up to date, or apply a change across them.
argument-hint: no arguments required
agent: agent
---

First, read `.github/instructions/repos.instructions.md` in full — it's the source of truth for
both what the `repos` map means and the Cross-Repo Change Workflow.

Then read `properties.yml` at the repo root and resolve its `repos` key (the org/repo list) and
`lineage` sub-key (parent → child chain). If `properties.yml` doesn't exist yet, tell the user to
run `/setup` first.

- If the user just wants to know what the related repos are, summarize the map and stop there.
- If the user wants a change applied to the related repos (e.g. "apply this to the related repos" /
  "update the related repos with this"), follow the Cross-Repo Change Workflow in
  `repos.instructions.md` against each repo in scope.

This command doubles as a recognition trigger: whenever the user says "related repos", "the repos",
"other repos", "pull all repos", or "pull the repos" about this vault's family (not generic talk about "the repository"), read
`repos.instructions.md` and act on it — even if they didn't explicitly run `/repos`.
