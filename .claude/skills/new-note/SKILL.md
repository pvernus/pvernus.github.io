---
name: new-note
description: Scaffold a new writing note in garden/notes/ with today's date and correct frontmatter
argument-hint: "[tag1 tag2 ...]"
allowed-tools: ["Read", "Write", "Glob", "Bash"]
---

# /new-note — New Writing Note

Scaffolds a new writing note in `garden/notes/` with today's date and correct frontmatter.
The file will be auto-renamed to `YYYY-MM-DD.qmd` (or `YYYY-MM-DD-N.qmd`) by `_pre-render.py`
on the next render.

## Input

Optional: space- or comma-separated tags.

```
/new-note                      → no tags
/new-note care ecology utopia  → tags: [care, ecology, utopia]
```

## Instructions

1. **Get today's date** in `YYYY-MM-DD` format using the system date.

2. **Count existing notes for today**: scan `garden/notes/*.qmd`, read each file's
   `date:` frontmatter field, count how many match today's date.
   Report: `"This will be note N for YYYY-MM-DD."` (where N = existing count + 1).

3. **Parse tags** from `$ARGUMENTS`: split on spaces and/or commas, strip whitespace.
   If no arguments, tags list is empty.

4. **Determine a safe filename**: try `garden/notes/YYYY-MM-DD-draft.qmd`.
   If that file already exists, try `YYYY-MM-DD-draft-2.qmd`, `-draft-3.qmd`, etc.

5. **Write the file** with this exact content (blank line after the closing `---`):

```
---
type: writing
title: ""
date: YYYY-MM-DD
tags: [tag1, tag2]
bibliography: _bib/library.json
---

```

   If no tags were provided, write `tags: []`.

6. **Report**:
   - Path of the created file
   - Note count for today
   - One-line reminder: `"_pre-render.py will rename this to YYYY-MM-DD.qmd on next render."`

## Notes

- Do NOT set `title:` — leave it as an empty string. `_pre-render.py` will set it to
  the date-based slug on render.
- The file must be in `garden/notes/`, not `garden/sources/` (those are auto-generated).
- If `garden/notes/` does not exist, create it.
