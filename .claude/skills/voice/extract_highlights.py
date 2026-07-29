"""Extract voice-study highlights from Zotero SQLite across all stores.

Stores:
  1. itemAnnotations on any attachment of the item (incl. secondary attachments)
  2. notes with <span style="background-color: X">TEXT</span>
  3. notes with <span class="highlight" ...>« TEXT »</span>  (Zotero annotation-derived)
  4. notes whose first line is 'Highlights export' (uncoloured e-reader paste)

Colour formats normalised: rgba(r,g,b,a) | #rrggbb | #rrggbbaa -> #rrggbb
"""
import sqlite3, os, re, html, json, sys, unicodedata

COLOUR = {
    "#ffd400": "yellow", "#a28ae5": "purple", "#2ea8e5": "blue",
    "#f19837": "orange", "#5fb236": "green", "#ff6666": "red",
}
STYLE_POOL = {"yellow", "purple", "blue"}      # feed sentence metrics
ANCHOR_COLOUR = "blue"                          # anchoring measure
MIN_WORDS = 8

# Citekeys come from argv, or from every @citekey in garden/notes/*.qmd when argv is empty.
def discover_keys():
    import glob
    ks = set()
    for f in glob.glob('garden/notes/*.qmd'):
        ks |= set(re.findall(r'@([A-Za-z][A-Za-z0-9_]*[0-9]{4}[a-z]?)', open(f, encoding='utf-8').read()))
    return sorted(ks)

KEYS = sys.argv[1:] or discover_keys()


def norm_colour(raw):
    raw = raw.strip().lower()
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", raw)
    if m:
        return "#%02x%02x%02x" % tuple(int(g) for g in m.groups())
    m = re.match(r"#([0-9a-f]{6})", raw)
    if m:
        return "#" + m.group(1)
    return None


def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("«", "").replace("»", "")
    return re.sub(r"\s+", " ", s).strip(" “”\"'.,;: ")


def wc(s):
    return len([w for w in re.split(r"\s+", s) if w])


def detect_lang(s):
    """FR vs EN by stopword hit-rate. Crude but adequate at sentence length."""
    fr = set("le la les des une un du de et est que qui dans pour sur pas ne se aux au "
             "par plus ce cette sont être leur nous il elle mais ou donc car".split())
    en = set("the of and to in that is are it for on with as this these was were be by "
             "not but or from their we they which has have".split())
    toks = [unicodedata.normalize("NFKD", w.lower().strip(".,;:!?()[]“”’"))
            for w in re.split(r"\s+", s)]
    f = sum(1 for t in toks if t in fr)
    e = sum(1 for t in toks if t in en)
    return "fr" if f > e else "en"


def parse_note(note_html):
    """Return list of (colour|None, text, shape) from one note.

    shape: 'export'  = store 3, sentinel, genuinely uncoloured
           'derived' = Zotero annotation-derived note (class="highlight")
           'span'    = hand-coloured background-color spans
    """
    out = []
    # kill huge url-encoded attribute payloads first
    body = re.sub(r'data-(annotation|citation|citation-items)="[^"]*"', "", note_html)

    first_line = strip_tags(body.split("</p>")[0])[:40] if "</p>" in body else ""
    if first_line.lower().startswith("highlights export"):
        for block in re.split(r"</p>|<br\s*/?>", body)[1:]:
            t = strip_tags(block)
            if wc(t) >= MIN_WORDS:
                out.append((None, t, "export"))
        return out

    # Zotero annotation-derived: <span class="highlight" ...>text</span>
    for m in re.finditer(r'<span class="highlight"[^>]*>(.*?)</span>\s*(?=<span class="citation"|</p>|<span class="highlight")',
                         body, re.S):
        inner = m.group(1)
        cols = [norm_colour(c) for c in re.findall(r"background-color:\s*([^;\"']+)", inner)]
        cols = [c for c in cols if c]
        t = strip_tags(inner)
        if wc(t) >= MIN_WORDS:
            dom = max(set(cols), key=cols.count) if cols else None
            out.append((dom, t, "derived"))
    if out:
        return out

    # plain coloured spans
    for m in re.finditer(r'<span style="[^"]*background-color:\s*([^;"\']+)[^"]*">(.*?)</span>', body, re.S):
        c = norm_colour(m.group(1))
        t = strip_tags(m.group(2))
        if c and wc(t) >= MIN_WORDS:
            out.append((c, t, "span"))
    return out


def main():
    p = os.path.expanduser(os.environ.get("ZOTERO_DATA_DIR", "~/Zotero") + "/zotero.sqlite")
    con = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
    c = con.cursor()
    ph = ",".join("?" * len(KEYS))
    c.execute(f"""select v.value, i.itemID from items i
        join itemData idt on idt.itemID=i.itemID
        join fields f on f.fieldID=idt.fieldID and f.fieldName='citationKey'
        join itemDataValues v on v.valueID=idt.valueID
        where v.value in ({ph})""", KEYS)
    items = dict(c.fetchall())

    recs = []
    for ck, iid in sorted(items.items()):
        # store 1 — annotations on any attachment
        c.execute("""select a.color, a.text from itemAnnotations a
                     join itemAttachments at on at.itemID=a.parentItemID
                     where at.parentItemID=? and a.text is not null""", (iid,))
        for colour, text in c.fetchall():
            t = re.sub(r"\s+", " ", (text or "")).strip()
            cn = norm_colour(colour or "")
            if t and wc(t) >= MIN_WORDS:
                recs.append(dict(ck=ck, store=1, shape="annot", colour=COLOUR.get(cn, cn), text=t))
        # stores 2-4 — notes
        c.execute("select note from itemNotes where parentItemID=?", (iid,))
        for (nh,) in c.fetchall():
            if not nh:
                continue
            for cn, t, shape in parse_note(nh):
                recs.append(dict(ck=ck, store={"export": 3}.get(shape, 2), shape=shape,
                                 colour=COLOUR.get(cn, cn) if cn else None, text=t))

    for r in recs:
        r["lang"] = detect_lang(r["text"])
        r["words"] = wc(r["text"])

    # MUST stay inside garden/.voice/ — gitignored. Highlight text is quoted source
    # material and must never land anywhere committable.
    outdir = os.path.join(os.getcwd(), "garden", ".voice")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "voice_highlights.jsonl"), "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- summary ----
    def tally(key, rows):
        d = {}
        for r in rows:
            d[r[key]] = d.get(r[key], 0) + 1
        return dict(sorted(d.items(), key=lambda kv: -kv[1]))

    print(f"items resolved: {len(items)}/{len(KEYS)}   retained highlights: {len(recs)}")
    print("by store :", tally("store", recs))
    print("by shape :", tally("shape", recs))
    print("by colour:", tally("colour", recs))
    print("by lang  :", tally("lang", recs))
    for lang in ("en", "fr"):
        pool = [r for r in recs if r["lang"] == lang and (r["colour"] in STYLE_POOL or r["colour"] is None)]
        if pool:
            mean = sum(r["words"] for r in pool) / len(pool)
            srt = sorted(r["words"] for r in pool)
            med = srt[len(srt) // 2]
            print(f"  {lang.upper()} style pool n={len(pool)}  mean={mean:.1f}w  median={med}w  "
                  f"sources={len({r['ck'] for r in pool})}")
    anchored = [r for r in recs if r["colour"] == ANCHOR_COLOUR]
    coloured = [r for r in recs if r["store"] != 3]
    print(f"  anchoring (blue share of coloured): {len(anchored)}/{len(coloured)}")
    print("per-source:", tally("ck", recs))


if __name__ == "__main__":
    main()
