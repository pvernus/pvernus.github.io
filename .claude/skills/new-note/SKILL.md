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
   If no arguments, tags list is empty. Write them lowercase and kebab-case
   (`climate-justice`, not `Climate Justice`) to match inherited tags.

   Do NOT look up Zotero tags by hand. `_pre-render.py` inherits them from the
   references the note cites on every render — see "Tag inheritance" below.
   Arguments are for tags that are yours alone (`FR`, `utopia`, a project name).

4. **Determine a safe filename**: try `garden/notes/YYYY-MM-DD-draft.qmd`.
   If that file already exists, try `YYYY-MM-DD-draft-2.qmd`, `-draft-3.qmd`, etc.

5. **Write the file** with this exact content (blank line after the closing `---`):

```
---
type: writing
title: ""
date: YYYY-MM-DD
tags: [tag1, tag2]
---

```

   If no tags were provided, write `tags: []`.

   Do NOT add a `bibliography:` field. `_quarto.yml` sets it project-wide to
   `garden/_cited.json`; a per-note field would override it with a path that
   does not exist in CI, and citations would render as literal `[@citekey]`.

6. **Report**:
   - Path of the created file
   - Note count for today
   - One-line reminder: `"_pre-render.py will rename this to YYYY-MM-DD.qmd on next render."`

## Tag inheritance

Tags are not something to research by hand — `_pre-render.py` adds them automatically.

On every render it reads the Zotero SQLite database, collects the tags of every
reference the note cites with `@citekey`, and merges them into `tags:`. A tag carries
over only if **at least 2** of the note's cited references share it, so a note's tags
reflect its recurring themes rather than every subject its sources touch. A note citing
a single tagged reference inherits that reference's tags outright.

Tags are normalized to lowercase kebab-case, and workflow markers (`/unread`, `To Read`),
plugin error tags (`⛔ No DOI found`), and JEL codes (`Q54`) are dropped.

**Inheritance only ever adds.** Tags already in the file are preserved — but a tag
removed by hand comes back on the next render if the citations still support it. To
suppress one permanently, remove it in Zotero or add it to `STATUS_TAGS` in
`_pre-render.py`.

Requires the Zotero database at `~/Zotero/zotero.sqlite` (override with
`ZOTERO_DATA_DIR`). Absent — as in CI — the step is skipped and tags are left alone.

## Notes

- Do NOT set `title:` — leave it as an empty string. `_pre-render.py` will set it to
  the date-based slug on render.
- The file must be in `garden/notes/`, not `garden/sources/` (those are auto-generated).
- If `garden/notes/` does not exist, create it.
