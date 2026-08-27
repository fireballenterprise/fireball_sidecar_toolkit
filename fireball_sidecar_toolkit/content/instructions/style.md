---
applyTo: "**"
---
# Markdown Style Standards

Rules for all markdown files created across this repository.

## Horizontal Rules

**Never use a standalone `---` line as a section divider in the body of a `.github/instructions/*.md`
file.** The only place `---` belongs is the YAML frontmatter delimiter (the opening and closing
`---` around `applyTo: "**"`) — never between headers. Headers and blank lines alone are enough
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

## Alphabetical Ordering

**Always order functions, tasks, methods, and list items alphabetically** unless execution order requires otherwise (e.g., a pipeline that must run step 1 before step 2).

This applies to:
- Invoke task functions within a task file
- Module-level functions within a Python file
- Dictionary keys, YAML keys, and list items where order is arbitrary
- Import groups are sorted by ruff — do not override

```python
# ✅ CORRECT — alphabetical
@task
def clean(...): ...

@task
def install(...): ...

@task
def restart(...): ...
```

```python
# ❌ WRONG — order of addition
@task
def install(...): ...

@task
def update(...): ...

@task
def clean(...): ...
```
