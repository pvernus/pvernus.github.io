#!/usr/bin/env python3
"""
Quarto pre-render script:
1. Auto-renames writing notes to YYYY-MM-DD[-N].qmd and syncs their title: field.
2. Propagates Zotero tags from cited references into writing note frontmatter.
3. Auto-generates and updates source notes in garden/sources/ from a Better BibTeX
   JSON export of the Zotero library (_bib/library.json).

Registered in _quarto.yml as:
  project:
    pre-render: _pre-render.py

Source notes are created when first cited in a writing note; their "Cited in" section
is updated on every subsequent render. "Related to" is populated from Zotero connexe
(dc:relation) via the Better BibTeX JSON relations field.

Tags come from the Zotero SQLite database rather than library.json, which carries no
tag data (Zotero's CSL JSON export drops them). Reads are read-only and safe while
Zotero is running; when the database is absent — as in CI — tag steps are skipped.
"""

import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LIBRARY_JSON = Path("_bib/library.json")
# Pruned CSL JSON holding only the works the garden actually cites. Unlike
# _bib/library.json (gitignored, local to Paul's Zotero) this file is committed,
# so pandoc can resolve @citekey when the site builds in CI.
CITED_JSON = Path("garden/_cited.json")
NOTES_DIR = Path("garden/notes")
SOURCES_DIR = Path("garden/sources")
STALE_HOURS = 24

ZOTERO_DIR = Path(os.environ.get("ZOTERO_DATA_DIR") or (Path.home() / "Zotero"))
ZOTERO_SQLITE = ZOTERO_DIR / "zotero.sqlite"

# A tag carries over to a note only if this many of its cited references share it.
# Notes citing a single tagged reference inherit that reference's tags outright.
TAG_MIN_REFS = 2

# Workflow and status tags — about Paul's reading queue, not about the subject.
STATUS_TAGS = {
    "read", "reading", "unread", "to-read", "toread", "to-print", "printed",
    "todo", "done", "wip", "draft", "important", "favorite", "favourite",
    "duplicate", "check", "cited", "skimmed",
}

# JEL classification codes (Q54, F63, …) — useful in Zotero, noise as note tags.
JEL_RE = re.compile(r'^[a-z]\d{1,2}$')

DATE_STEM_RE = re.compile(r'^\d{4}-\d{2}-\d{2}(?:-(\d+))?$')
# @citekey references, ignoring @ inside URLs (e.g. youtube.com/@user).
# Internal : and . are allowed, but a key never ends on punctuation — otherwise
# "@aklin2020: notes that" would capture the key as "aklin2020:". This mirrors
# how pandoc itself delimits citation keys.
CITEKEY_RE = re.compile(r'(?<!/)@(\w[\w-]*(?:[:.][\w-]+)*)')
TAGS_LINE_RE = re.compile(r'^tags:\s*\[([^\]]*)\]', re.MULTILINE)


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


def _parse_fm_tags(text):
    m = TAGS_LINE_RE.search(text)
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(",") if t.strip()]


def _set_fm_tags(text, tags):
    line = f"tags: [{', '.join(tags)}]"
    if TAGS_LINE_RE.search(text):
        return TAGS_LINE_RE.sub(lambda _: line, text, count=1)
    # No tags: field yet — insert it just before the frontmatter's closing ---.
    return re.sub(
        r'\A(---\n.*?\n)(---\n)',
        lambda m: m.group(1) + line + "\n" + m.group(2),
        text,
        count=1,
        flags=re.DOTALL,
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
# Zotero tags
# ---------------------------------------------------------------------------

def normalize_tag(raw):
    """Fold a Zotero tag to the garden's kebab-case convention.

    Returns None for tags that should not propagate: workflow markers (/unread,
    "To Read"), plugin error tags ("⛔ No DOI found"), and JEL codes.
    """
    t = str(raw).strip()
    # Anything not starting with a word character is a marker, not a subject:
    # "/unread", "⛔ No DOI found", "* starred".
    if not t or not re.match(r'\w', t, re.UNICODE):
        return None
    t = re.sub(r'[\s_/]+', '-', t.lower())
    t = re.sub(r'[^\w-]', '', t, flags=re.UNICODE)
    t = re.sub(r'-{2,}', '-', t).strip('-')
    if not t or t in STATUS_TAGS or JEL_RE.match(t):
        return None
    return t


def load_zotero_tags():
    """Return {citekey: {tag, ...}} read from the Zotero SQLite database.

    citationKey is a native Zotero field, so this needs no Better BibTeX export.
    Opened read-only and immutable, which is safe while Zotero holds the file.
    Returns {} when the database is missing or unreadable.
    """
    if not ZOTERO_SQLITE.exists():
        print(
            f"garden: {ZOTERO_SQLITE} not found — skipping tag inheritance.\n"
            "        Set ZOTERO_DATA_DIR if your Zotero data lives elsewhere."
        )
        return {}

    query = """
        select ck.value, t.name
        from itemData idt
        join itemDataValues ck on ck.valueID = idt.valueID
        join fields f on f.fieldID = idt.fieldID and f.fieldName = 'citationKey'
        join itemTags it on it.itemID = idt.itemID
        join tags t on t.tagID = it.tagID
        where idt.itemID not in (select itemID from deletedItems)
    """
    tags = defaultdict(set)
    try:
        con = sqlite3.connect(
            "file:" + ZOTERO_SQLITE.as_posix() + "?mode=ro&immutable=1", uri=True
        )
        try:
            for citekey, raw in con.execute(query):
                tag = normalize_tag(raw)
                if tag:
                    tags[citekey].add(tag)
        finally:
            con.close()
    except sqlite3.Error as exc:
        print(f"garden: could not read Zotero tags ({exc}) — skipping tag inheritance")
        return {}

    print(f"garden: Zotero tags loaded for {len(tags)} citekeys")
    return dict(tags)


def propagate_tags(zotero_tags):
    """Merge tags from each writing note's cited references into its frontmatter.

    A tag must be shared by TAG_MIN_REFS of the note's cited references to carry
    over, so a note's tags reflect its recurring themes rather than every subject
    touched by every source. Notes citing one tagged reference inherit its tags.

    Existing tags are always preserved — this only ever adds.
    """
    if not zotero_tags:
        return

    touched = 0
    for path in sorted(NOTES_DIR.glob("*.qmd")):
        text = path.read_text(encoding="utf-8")
        cited = {k: zotero_tags[k] for k in set(CITEKEY_RE.findall(text))
                 if k in zotero_tags}
        if not cited:
            continue

        counts = Counter(tag for tags in cited.values() for tag in tags)
        threshold = 1 if len(cited) == 1 else TAG_MIN_REFS
        inherited = sorted(tag for tag, n in counts.items() if n >= threshold)

        existing = _parse_fm_tags(text)
        have = {t.lower() for t in existing}
        added = [t for t in inherited if t not in have]
        if not added:
            continue

        path.write_text(_set_fm_tags(text, existing + added), encoding="utf-8")
        print(f"garden: tagged   {path.name} +{len(added)} ({', '.join(added)})")
        touched += 1

    if touched:
        print(f"garden: {touched} note(s) gained tags from cited references.")


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
        for key in CITEKEY_RE.findall(text):
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


def fmt_tags(key, zotero_tags):
    """Tags for a source note, read from the Zotero database.

    library.json is not a tag source: Zotero's CSL JSON export drops tags, so no
    entry carries a keyword field.
    """
    return sorted(zotero_tags.get(key, ()))


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
# Cited-works bibliography
# ---------------------------------------------------------------------------

def emit_cited_json(citations, by_key):
    """Write garden/_cited.json — the CSL JSON entries the garden cites.

    _bib/library.json is gitignored, so without this the published site has no
    bibliography and every @citekey renders literally as "[@latour2017]". Writing
    a pruned copy keeps the committed file small and free of uncited material.

    Skipped when the library is unavailable, leaving the committed file intact.
    """
    if not by_key:
        return
    entries = [by_key[k] for k in sorted(citations) if k in by_key]
    if not entries:
        return

    payload = json.dumps(entries, ensure_ascii=False, indent=2) + "\n"
    previous = CITED_JSON.read_text(encoding="utf-8") if CITED_JSON.exists() else None
    if payload != previous:
        CITED_JSON.write_text(payload, encoding="utf-8")
        print(f"garden: _cited.json -> {len(entries)} works")

    missing = sorted(k for k in citations if k not in by_key)
    if missing:
        print(
            f"garden: ⚠  {len(missing)} cited key(s) missing from library.json — "
            f"these render unresolved: {', '.join(missing)}"
        )


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
        tags = _parse_fm_tags(text)
        citekeys = set(CITEKEY_RE.findall(text))
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


def build_source_note(key, item, related_keys, by_key, citing_notes, zotero_tags):
    title = item.get("title", "Untitled").replace('"', "'")
    tags_str = ", ".join(fmt_tags(key, zotero_tags))
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

    # Step 3: Inherit tags from cited references (needs Zotero, not library.json).
    # Runs before links.json so the shared-tag graph sees the new tags.
    zotero_tags = load_zotero_tags()
    propagate_tags(zotero_tags)

    # Step 4: Load library if available.
    has_library = check_library()
    by_key, uri_to_key = load_library() if has_library else ({}, {})

    # Step 5: Emit links.json + the committed bibliography of cited works.
    emit_links_json(citations, by_key)
    emit_cited_json(citations, by_key)

    # Step 6: Source note generation (requires library).
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
                build_source_note(key, item, related_keys, by_key, citing_notes,
                                  zotero_tags),
                encoding="utf-8",
            )
            print(f"garden: created  {dest.name}")
            created += 1
        else:
            old = dest.read_text(encoding="utf-8")
            new = update_cited_in(old, citing_notes)
            tags = fmt_tags(key, zotero_tags)
            if tags and _parse_fm_tags(new) != tags:
                new = _set_fm_tags(new, tags)
            if new != old:
                dest.write_text(new, encoding="utf-8")
                print(f"garden: updated  {dest.name}")
                updated += 1

    if created or updated or skipped:
        print(f"garden: {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
