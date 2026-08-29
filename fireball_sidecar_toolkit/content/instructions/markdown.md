---
description: "Use when writing or editing any Markdown file. Covers horizontal rules, headers, verbosity, and README structure."
applyTo: "**/*.md"
---
# Markdown Style Standards
Rules for every Markdown file in the repo.

## Horizontal Rules
**Never use a standalone `---` line as a section divider in the body of a `.github/instructions/*.md`
file.** The only place `---` belongs is the YAML frontmatter delimiter (the opening and closing
`---` around `applyTo`) — never between headers. Headers and blank lines alone are enough
visual separation.

```markdown
# ✅ CORRECT
---
applyTo: "**"
---
# File Title
Intro sentence.

## Section One
Content.

## Section Two
Content.
```

```markdown
# ❌ WRONG
---
applyTo: "**"
---
# File Title

---

## Section One
Content.

---

## Section Two
Content.
```

## Headers
**Do not add a blank line after any header (`#`, `##`, `###`, etc.).** Content begins on the very next line.

```markdown
# ✅ CORRECT
## Section
- bullet one
- bullet two

## Another Section
Content starts here immediately.

| col1 | col2 |
|------|------|
| a    | b    |
```

```markdown
# ❌ WRONG
## Section

- bullet one

## Another Section

Content with extra blank line above.
```

Blank lines **before** a header (to separate sections) are fine and expected.

## Verbosity
**When asked to create a file, keep it non-verbose unless the user says otherwise.** No preamble,
no restating the request, no filler explanation. Include only the substantive content. Add
structure, context, or commentary only when the user asks for it or the file's purpose requires it.

## README Files
- Lead with a short one-sentence description of the thing being documented
- The repo `README.md` includes: Setup, Project Structure, Invoke Tasks, and Modules sections
- Show invoke commands in fenced `sh` blocks (`uv run --no-sync invoke ...`)
- Keep it concise — link out rather than duplicating content that lives elsewhere

## Alphabetical Ordering
For code ordering rules (functions, invoke tasks, constants, dict/YAML keys), see
`python.instructions.md`.
