---
name: cleanup
description: Use after a PR merges, or to tidy a repo — cleans up the merged feature branch (switch to default, pull, delete) then sweeps local build/cache trash and orphaned dirs. `all` does it across the family. Equivalent to /cleanup.
hints:
  - cleanup
  - clean up the repo
  - clean up local trash
  - sweep stale caches
  - remove orphaned dirs
instructions:
  - .ai/toolkit/instructions/repos.md
commands:
  - .ai/toolkit/commands/cleanup.md
---
