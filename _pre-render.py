#!/usr/bin/env python3
"""
Quarto pre-render script:
1. Auto-renames writing notes to YYYY-MM-DD[-N].qmd and syncs their title: field.
2. Auto-generates and updates source notes in garden/sources/ from a Better BibTeX
   JSON export of the Zotero library (_bib/library.json).

Registered in _quarto.yml as:
  project:
    pre-render: _pre-render.py

Source notes are created when first cited in a writing note; their "Cited in" section
is updated on every subsequent render. "Related to" is populated from Zotero connexe
(dc:relation) via the Better BibTeX JSON relations field.
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LIBRARY_JSON = Path("_bib/library.json")
NOTES_DIR = Path("garden/notes")
SOURCES_DIR = Path("garden/sources")
STALE_HOURS = 24

DATE_STEM_RE = re.compile(r'^\d{4}-\d{2}-\d{2}(?:-(\d+))?$')


# ---------------------------------------------------------------------------
# Writing note renaming
# ---------------------------------------------------------------------------

def _parse_fm_date(text):
    m = re.search(r'^date:\s*["\']?(\d{4}-\d{2}-\d{2})["\']?', text, re.MULTILINE)
    return m.group(1) if m else None


def _set_fm_title(text, new_title):
    return re.sub(
        r'^(title:\s*).*$',
        f'\\1"{new_title}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )


def rename_writing_notes():
    """Rename notes to YYYY-MM-DD[-N].qmd and sync the title: field.

    Single note on a date  → YYYY-MM-DD.qmd  / title: "YYYY-MM-DD"
    Multiple notes on date → YYYY-MM-DD-1.qmd, YYYY-MM-DD-2.qmd, …
    Notes without a date: field are left untouched.
    Already-dated filenames keep their relative order; new (undated) filenames
    are appended in alphabetical order.
    """
    notes = []
    for path in NOTES_DIR.glob("*.qmd"):
        text = path.read_text(encoding="utf-8")
        date = _parse_fm_date(text)
        if date is None:
            continue
        notes.append((path, date, text))

    by_date = defaultdict(list)
    for path, date, text in notes:
        by_date[date].append((path, text))

    for date, group in by_date.items():
        def sort_key(item):
            path, _ = item
            m = DATE_STEM_RE.match(path.stem)
            if m:
                return (0, int(m.group(1)) if m.group(1) else 1, path.stem)
            return (1, 0, path.stem)

        group.sort(key=sort_key)
        n = len(group)

        for i, (path, text) in enumerate(group):
            new_stem = date if n == 1 else f"{date}-{i + 1}"
            new_path = NOTES_DIR / f"{new_stem}.qmd"
            new_text = _set_fm_title(text, new_stem)

            needs_rename = new_path != path
            needs_title  = new_text != text

            if needs_rename and needs_title:
                new_path.write_text(new_text, encoding="utf-8")
                path.unlink()
                print(f"garden: renamed  {path.name} -> {new_path.name}")
            elif needs_rename:
                path.rename(new_path)
                print(f"garden: renamed  {path.name} -> {new_path.name}")
            elif needs_title:
                path.write_text(new_text, encoding="utf-8")
                print(f"garden: retitled {path.name}")


# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------

def check_library():
    if not LIBRARY_JSON.exists():
        print(
            "garden: _bib/library.json not found — skipping source note generation.\n"
            "        Export Zotero library as Better BibTeX JSON to _bib/library.json to enable."
        )
        return False
    age = datetime.now() - datetime.fromtimestamp(LIBRARY_JSON.stat().st_mtime)
    if age > timedelta(hours=STALE_HOURS):
        hours = int(age.total_seconds() / 3600)
        print(f"garden: ⚠  library.json is {hours}h old — open Zotero to refresh")
    return True


def load_library():
    """Return (by_key, uri_to_key) where by_key maps citekey -> item dict."""
    with open(LIBRARY_JSON, encoding="utf-8") as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get("references", data.get("items", []))
    by_key = {}
    uri_to_key = {}
    for item in items:
        key = item.get("id") or item.get("citekey")
        if not key:
            continue
        by_key[key] = item
        uri = item.get("uri")
        if uri:
            uri_to_key[uri] = key
            # Index by last path segment too (Zotero item key)
            uri_to_key[uri.rstrip("/").split("/")[-1]] = key
    return by_key, uri_to_key


# ---------------------------------------------------------------------------
# Writing note scanning
# ---------------------------------------------------------------------------

def scan_citations():
    """Scan garden/notes/*.qmd for @citekey references.

    Returns dict: citekey -> list of (path, title), deduplicated per note.
    Excludes @ symbols embedded in URLs (e.g. youtube.com/@user).
    """
    result = {}
    for path in sorted(NOTES_DIR.glob("*.qmd")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
        title = m.group(1).strip("\"'") if m else path.stem
        seen_in_note = set()
        for key in re.findall(r'(?<!/)@([\w:.-]+)', text):
            if key not in seen_in_note:
                result.setdefault(key, []).append((path, title))
                seen_in_note.add(key)
    return result


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def fmt_authors(item):
    people = item.get("author") or item.get("editor") or []
    names = [p.get("family", "") for p in people if p.get("family")]
    if not names:
        return "Unknown"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    return f"{names[0]} et al."


def fmt_year(item):
    parts = item.get("issued", {}).get("date-parts", [[]])
    return str(parts[0][0]) if parts and parts[0] else ""


def fmt_tags(item):
    kw = item.get("keyword", "")
    if isinstance(kw, list):
        return [k.strip() for k in kw if k.strip()]
    return [k.strip() for k in str(kw).split(",") if k.strip()]


_TYPE_LABELS = {
    "article-journal": "Article",
    "book": "Book",
    "chapter": "Book chapter",
    "report": "Report",
    "webpage": "Webpage",
    "blogPost": "Blog post",
    "thesis": "Thesis",
    "preprint": "Preprint",
    "conferencePaper": "Conference paper",
    "videoRecording": "Video",
    "podcast": "Podcast",
    "radioBroadcast": "Radio broadcast",
    "document": "Document",
    "magazineArticle": "Magazine article",
    "newspaperArticle": "Newspaper article",
}


def fmt_info(item):
    """Return (info_line, link_md) for the source note body."""
    itype = _TYPE_LABELS.get(item.get("type", ""), item.get("type", ""))
    venue = (item.get("container-title") or
             item.get("collection-title") or
             item.get("publisher") or
             item.get("institution") or "")
    info = " · ".join(p for p in [itype, venue] if p)
    doi = item.get("DOI", "")
    url = item.get("URL", "")
    link = f"[DOI](https://doi.org/{doi})" if doi else (f"[URL]({url})" if url else "")
    return info, link


def fmt_abstract(item):
    return (item.get("abstract") or "").strip()


def get_related_keys(item, by_key, uri_to_key):
    """Extract connexe (related) citekeys from the Better BibTeX JSON relations field.

    Better BibTeX JSON stores Zotero relations as:
      "relations": {"dc:relation": ["https://zotero.org/users/.../items/ITEMKEY", ...]}

    If the relations field is absent or empty, returns [].
    """
    related = []
    relations = item.get("relations", {})
    if isinstance(relations, dict):
        uris = relations.get("dc:relation", [])
        if isinstance(uris, str):
            uris = [uris]
        for uri in uris:
            key = uri_to_key.get(uri)
            if not key:
                # Fall back to last URI segment (Zotero item key)
                key = uri_to_key.get(uri.rstrip("/").split("/")[-1])
            if key and key in by_key:
                related.append(key)
    elif isinstance(relations, list):
        related = [r for r in relations if isinstance(r, str) and r in by_key]
    return related


# ---------------------------------------------------------------------------
# Network graph data
# ---------------------------------------------------------------------------

def emit_links_json(citations, by_key):
    """Write garden/links.json for the force-directed network visualisation.

    Nodes: writing notes (type=writing) + cited source notes (type=source).
    Edges:
      cites   — writing note -> source note it cites
      shared  — writing note <-> writing note sharing tags or citekeys
    Works without by_key (library absent): source nodes get citekey as title.
    """
    nodes = []
    edges = []
    seen_sources = set()

    writing_map = {}  # stem -> {tags: set, citekeys: set}
    for path in sorted(NOTES_DIR.glob("*.qmd")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
        title = m.group(1).strip("\"'") if m else path.stem
        m = re.search(r'^tags:\s*\[([^\]]*)\]', text, re.MULTILINE)
        raw_tags = [t.strip() for t in m.group(1).split(",")] if m else []
        tags = [t for t in raw_tags if t]
        citekeys = set(re.findall(r'@([\w:.-]+)', text))
        stem = path.stem
        nodes.append({
            "id": stem,
            "type": "writing",
            "title": title,
            "tags": tags,
            "path": f"garden/notes/{stem}.html",
        })
        writing_map[stem] = {"tags": set(tags), "citekeys": citekeys}

    # Source nodes + cites edges
    for key, citing_notes in citations.items():
        if key not in seen_sources:
            seen_sources.add(key)
            item = by_key.get(key, {})
            s_title = (item.get("title", key)[:70] if item else key)
            nodes.append({
                "id": key,
                "type": "source",
                "title": s_title,
                "path": f"garden/sources/{key}.html",
            })
        for path, _ in citing_notes:
            edges.append({"source": path.stem, "target": key, "type": "cites"})

    # Writing <-> writing (shared tags or shared citekeys)
    ids = list(writing_map.keys())
    for i, id1 in enumerate(ids):
        for id2 in ids[i + 1:]:
            d1, d2 = writing_map[id1], writing_map[id2]
            if (d1["tags"] & d2["tags"]) or (d1["citekeys"] & d2["citekeys"]):
                edges.append({"source": id1, "target": id2, "type": "shared"})

    out = NOTES_DIR.parent / "links.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)
    print(f"garden: links.json -> {len(nodes)} nodes, {len(edges)} edges")


# ---------------------------------------------------------------------------
# Source note rendering
# ---------------------------------------------------------------------------

def related_lines(related_keys, by_key):
    if not related_keys:
        return ["<!-- none yet -->"]
    lines = []
    for key in related_keys:
        ritem = by_key[key]
        label = fmt_authors(ritem)
        year = fmt_year(ritem)
        if year:
            label = f"{label} ({year})"
        snippet = ritem.get("title", key)[:60]
        lines.append(f"- [{label}]({key}.qmd) — {snippet}")
    return lines


def cited_lines(citing_notes):
    if not citing_notes:
        return ["<!-- none yet -->"]
    return [f"- [{title}](../notes/{path.name})" for path, title in citing_notes]


def build_source_note(key, item, related_keys, by_key, citing_notes):
    title = item.get("title", "Untitled").replace('"', "'")
    tags = fmt_tags(item)
    tags_str = ", ".join(tags)
    related_block = "\n".join(related_lines(related_keys, by_key))
    cited_block = "\n".join(cited_lines(citing_notes))

    abstract = fmt_abstract(item)

    publisher = (item.get("publisher") or item.get("institution") or
                 item.get("container-title") or "")
    year      = fmt_year(item)
    isbn      = item.get("ISBN", "")
    doi       = item.get("DOI", "")

    author = fmt_authors(item)

    # YAML extra fields (machine-readable)
    extra_yaml = ""
    if publisher: extra_yaml += f'publisher: "{publisher.replace(chr(34), chr(39))}"\n'
    if year:      extra_yaml += f"year: {year}\n"
    if isbn:      extra_yaml += f'isbn: "{isbn}"\n'
    if doi:       extra_yaml += f'doi: "{doi}"\n'

    # Body display fields
    meta_fields = []
    if author and author != "Unknown":
        meta_fields.append(f"**Author:** {author}")
    if publisher:
        meta_fields.append(f"**Publisher:** {publisher}")
    if year:
        meta_fields.append(f"**Date:** {year}")
    if isbn:
        meta_fields.append(f"**ISBN:** {isbn}")
    if doi:
        meta_fields.append(f"**DOI:** [{doi}](https://doi.org/{doi})")

    meta_block     = "  \n".join(meta_fields) + "\n\n" if meta_fields else ""
    abstract_block = f"**Abstract:** {abstract}\n\n" if abstract else ""

    return (
        f'---\n'
        f'type: source\n'
        f'title: "{title}"\n'
        f'zotero-key: {key}\n'
        f'tags: [{tags_str}]\n'
        f'{extra_yaml}'
        f'---\n\n'
        f'{meta_block}'
        f'{abstract_block}'
        f'## Related to\n\n'
        f'{related_block}\n\n'
        f'## Cited in\n\n'
        f'{cited_block}\n'
    )


def update_cited_in(content, citing_notes):
    """Replace the content of the ## Cited in section, preserving everything after it."""
    block = "\n".join(cited_lines(citing_notes))
    # Match from "## Cited in\n\n" to the next heading or end of file
    updated = re.sub(
        r'(## Cited in\n\n).*?(\Z|(?=\n## ))',
        lambda m: m.group(1) + block + "\n",
        content,
        flags=re.DOTALL,
    )
    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Step 1: Rename notes (no library needed).
    if NOTES_DIR.exists():
        rename_writing_notes()

    if not NOTES_DIR.exists():
        return

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    # Step 2: Scan citations (no library needed).
    citations = scan_citations()

    # Step 3: Load library if available.
    has_library = check_library()
    by_key, uri_to_key = load_library() if has_library else ({}, {})

    # Step 4: Emit links.json (works with or without library).
    emit_links_json(citations, by_key)

    # Step 5: Source note generation (requires library).
    if not has_library:
        return

    created = updated = skipped = 0

    for key, citing_notes in citations.items():
        if key not in by_key:
            print(f"garden: @{key} not found in library.json — skipping")
            skipped += 1
            continue

        item = by_key[key]
        related_keys = get_related_keys(item, by_key, uri_to_key)
        dest = SOURCES_DIR / f"{key}.qmd"

        if not dest.exists():
            dest.write_text(
                build_source_note(key, item, related_keys, by_key, citing_notes),
                encoding="utf-8",
            )
            print(f"garden: created  {dest.name}")
            created += 1
        else:
            old = dest.read_text(encoding="utf-8")
            new = update_cited_in(old, citing_notes)
            if new != old:
                dest.write_text(new, encoding="utf-8")
                print(f"garden: updated  {dest.name}")
                updated += 1

    if created or updated or skipped:
        print(f"garden: {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
