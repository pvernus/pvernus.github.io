# Memory — Personal Academic Website

## [LEARN:zotero] Better BibTeX JSON is a plain list

Better BibTeX JSON export from Zotero is a top-level JSON array, not a dict.
Always guard with `isinstance(data, list)` before calling `.get()`.

## [LEARN:garden] Pre-render pipeline order matters

`_pre-render.py` must run `rename_writing_notes()` before `scan_citations()` so
source notes reference the final date-based filenames, not the original slugs.
`emit_links_json()` runs after scan — it depends on citations but not the library.
Source note generation is the only step that strictly requires `_bib/library.json`.

## [LEARN:quarto] Custom frontmatter fields are not rendered by journal theme

Only standard Quarto fields (`title:`, `author:`, `date:`) are displayed on the
rendered HTML page. Custom fields (`publisher:`, `isbn:`, `doi:`) are stored in
frontmatter for machine use but must be repeated in the body for human display.
