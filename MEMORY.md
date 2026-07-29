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

## [LEARN:skill-design] Tier thresholds must be derived from the achievable population

A skill that gates progress on a counter needs its tiers checked against how many
items can actually reach the counter. The `/voice` skill promotes rules from
`[provisional]` after 3 confirmations, then sets maturity tiers at `<15` /
`15–49` / `≥50` *promoted rules* — but its profile holds 5 rules, and the
confirmation loop only promotes existing rules, never creates them. The second
tier is unreachable by design, so the label reads `bootstrap` forever.

**The trap:** the counter and the thresholds were specified independently. The
counter is over a population one operation grows (`rule-add`) and another merely
transforms (`rule-confirm`) — but the user's routine loop only ever runs the
second.

**When writing any gate:** ask what the ceiling is if every pending item passes.
If that ceiling sits below the next threshold, either the threshold is wrong or
the loop is missing a way to grow the population. Applies to quality gates,
maturity levels, and confidence counters alike — a progress signal that cannot
advance is worse than none, because it reads as failure rather than as
mis-specification.

## [LEARN:zotero] Zotero's CSL JSON export drops tags — the database is the only source

Tags do not survive Zotero's CSL JSON export. A pipeline reading a `keyword`
field from that export finds it on **zero** items — in this library, 0 of 9,327.
The code looked correct and had never once worked.

Tags live in `zotero.sqlite`. Since Zotero 7 `citationKey` is a *native* field,
so `citekey → tags` joins without any Better BibTeX dependency:

```sql
select ck.value, t.name from itemData idt
join itemDataValues ck on ck.valueID = idt.valueID
join fields f on f.fieldID = idt.fieldID and f.fieldName = 'citationKey'
join itemTags it on it.itemID = idt.itemID
join tags t on t.tagID = it.tagID
where idt.itemID not in (select itemID from deletedItems)
```

Open `file:...?mode=ro&immutable=1` — safe to read while Zotero is running.

**The general lesson:** when a feature "has never worked", check whether its
*input* ever existed before debugging the logic. Count the field across the
whole dataset — a zero tells you more than any amount of reading the function.

**Second lesson, if you inherit tags:** raw tag vocabularies are dirty. Naive
union gave one note 64 tags, including `/unread`, `To Read`, `⛔ No DOI found`,
JEL codes, and three casings of one concept. Require a tag to appear on ≥2
sources before it carries over, and drop anything not starting with a word
character.

## [LEARN:ci] A gitignored input silently breaks the *published* build only

`_bib/library.json` is gitignored, so the bibliography existed locally and
nowhere else. Every page rendered perfectly on the dev machine and published
with literal `[@latour2017]` where citations should be. The build stayed green —
pandoc logs unresolved citations as warnings and still exits 0.

**Fix pattern:** commit a *pruned derivative* rather than the gitignored source.
A generated `_cited.json` holding only the works actually cited is small, free of
private material, and is the only bibliography CI ever needs.

**Two traps that follow:**
- Set `bibliography` once at project level. A per-document field silently
  overrides it with a path CI does not have — the original bug.
- The derivative and its consumers must be committed **together**. Ship a note
  whose new citation is not yet in the committed bibliography and it renders raw.

Generalises to any build-time data dependency: fonts, schemas, lockfiles. If it
is gitignored and the build "works", the build is working only for you.

## [LEARN:d3] `forceCenter` does not hold disconnected components together

`forceCenter` translates the centroid to a point. It applies **no attractive
force**. `forceManyBody` meanwhile repels every pair at unbounded range. Any
graph with two components that share no edge therefore pushes itself apart until
a cluster leaves the viewport — silently, since nothing errors.

Three fixes, best combined:
1. `forceManyBody().distanceMax(300)` — repulsion stays local to a cluster
2. `forceX(W/2)` / `forceY(H/2)` at low strength — real centring force
3. Clamp positions in the tick handler — a hard bound, correct by construction

Worth verifying headlessly: `d3-force` runs under Node with no DOM, so you can
tick the real graph to convergence and assert every node is in frame instead of
eyeballing a browser.

## [LEARN:quarto] Custom frontmatter fields are not rendered by journal theme

Only standard Quarto fields (`title:`, `author:`, `date:`) are displayed on the
rendered HTML page. Custom fields (`publisher:`, `isbn:`, `doi:`) are stored in
frontmatter for machine use but must be repeated in the body for human display.

## [LEARN:data] An empty result from one access path is not absence of data

Ran an extraction that concluded a source library's entire French half was
unannotated, and filed 14 sources as "nothing to learn". The highlights existed.
They lived in a **second storage location** the query never touched — and a third
existed too. The first pass captured 32% of the available signal and reported the
other 68% as absent.

The failure is silent by construction: an empty result and a genuinely empty
store are indistinguishable from the call site. Nothing errors.

Before concluding data does not exist:
- **Enumerate storage locations, not queries.** The same logical record often has
  several representations — a structured table, an embedded markup span, a
  plain-text export — written by different tools at different times.
- **Distrust a clean negative that fits a story.** "The FR half is unannotated"
  had a plausible explanation ready (read in print, not on screen), which is
  exactly why it survived unchallenged.
- **Check the API's own scope.** The library call read annotations on an item's
  *primary* attachment only; items with a second attachment silently lost theirs.

State the base a statistic was computed over, every time. "32% carry a named
actor" and "32% of the third of the data I could see" are different claims.

## [LEARN:security] Assert a generated file's write path against gitignore

Wrote a tool that extracted quoted passages from copyrighted sources. The skill
governing it stated plainly that this text must never reach a commit. The tool
defaulted to writing its output *next to itself* — inside the repo, in a tracked
directory. The invariant and its violation shipped in the same change.

Caught incidentally, by reading `git status` during unrelated session capture.

For any tool emitting a derivative of sensitive input:
- Pin the output directory explicitly and comment *why* it must stay there.
- Verify with `git check-ignore -v <path>` — it prints the matching rule, so a
  pass is evidence rather than an absence of failure.
- Treat `os.path.dirname(__file__)` as a smell for output. It is convenient for
  a script living in a scratch dir and wrong for one living in the repo.

The general shape: a rule written in prose in one file cannot enforce anything
about code in another. If an invariant matters, something must assert it.
