# Memory — Personal Academic Website

## [LEARN:zotero] Better BibTeX JSON is a plain list

Better BibTeX JSON export from Zotero is a top-level JSON array, not a dict.
Always guard with `isinstance(data, list)` before calling `.get()`.

## [LEARN:garden] Pre-render pipeline order matters

`_pre-render.py` must run `rename_writing_notes()` before `scan_citations()` so
source notes reference the final date-based filenames, not the original slugs.
`emit_links_json()` runs after scan — it depends on citations but not the library.
Source note generation is the only step that strictly requires `_bib/library.json`.

**Consequence for CI:** `_bib/` is gitignored, so the build server never has the
library and source-note generation silently no-ops there. `links.json` *is*
rebuilt in CI; `garden/sources/*.qmd` are *not*. Whatever `## Cited in` blocks
you commit are exactly what ships — verify them locally before pushing.

## [LEARN:quarto] Without an explicit `render:` list, Quarto publishes every `.md`

A Quarto project with no `project.render` key renders **all** `.qmd` *and* `.md`
files it finds — including `CLAUDE.md`, `MEMORY.md`, and anything under
`quality_reports/`. These become live pages (`/CLAUDE.html`, `/MEMORY.html`).
Underscore-prefixed files (`_notes.md`) are the only ones skipped by default.

**Fix:** declare the allowlist explicitly.
```yaml
project:
  render:
    - "**/*.qmd"
```
Trade-off: any `.md` that *should* publish must then be listed by name. Worth it —
the failure mode is silent and leaks internal working files.

## [LEARN:seo] `robots.txt` Disallow prevents de-indexing, it doesn't cause it

`Disallow` controls *crawling*, not *indexing*. Adding it for an already-indexed
page stops the crawler from refetching, so it never observes the 404 — the stale
entry persists, often shown as a bare URL with "No information is available."
A disallowed URL can also be indexed from inbound links alone, never having been read.

**To remove an indexed page:** leave it crawlable and let it 404/410, or serve
`noindex`. The removal signal has to be *visible* to the crawler.

## [LEARN:git] `git status` can hide working-tree edits (racy-timestamp stat cache)

Git skips content comparison when a file's mtime matches its index entry, so a
real edit can stay invisible until an unrelated command re-stats the file. A
`garden.qmd` prose change surfaced only after a script touched the directory.

Before concluding a tree is clean — especially prior to a selective commit — run
`git diff` rather than trusting `git status` alone.

## [LEARN:quarto] Custom frontmatter fields are not rendered by journal theme

Only standard Quarto fields (`title:`, `author:`, `date:`) are displayed on the
rendered HTML page. Custom fields (`publisher:`, `isbn:`, `doi:`) are stored in
frontmatter for machine use but must be repeated in the body for human display.
