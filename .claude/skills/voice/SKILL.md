---
name: voice
description: Develop and apply a personal writing voice for garden/notes/. Four sub-modes — init (bootstrap a voice profile from a corpus of admired writers), edit (review a draft against the profile), study (mine Zotero highlights on cited sources for candidate rules), mentor (ask draft-specific questions, including forced-choice sentence pairs, and sediment answers into the profile after 3 converging confirmations).
argument-hint: "init | edit <path> | study | mentor"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "AskUserQuestion", "mcp__zotero__zotero_search_by_citation_key", "mcp__zotero__zotero_get_annotations"]
---

# /voice — Writing Voice Workflow

*v1.1 — Bootstrap, apply, and iteratively refine a personal writing voice for `garden/notes/`*

Four functions, one shared profile:

1. **`/voice init`** — bootstrap or rebuild `garden/.voice/profile.md` from `garden/.voice/corpus/` (re-runnable as corpus grows)
2. **`/voice edit <path>`** — review a draft note; write a separate review file with grammar/syntax fixes and a profile-fit score
3. **`/voice study`** — mine Zotero annotations on the sources the garden cites; append candidate rules to `garden/.voice/candidates.md`. Observes only; never touches the profile
4. **`/voice mentor`** — ask 2–3 draft-specific questions, including forced-choice sentence pairs seeded from `candidates.md`; log answers; sediment confirmed rules into the profile after **≥3 converging decisions**

Profile, corpus, candidates, and decisions live under `garden/.voice/` (gitignored). Reviews live under `garden/notes/.review/` (gitignored).

## Input

`$ARGUMENTS` — one of: `init`, `edit <path>`, `study`, `mentor`.

## Instructions

Read the sub-mode from `$ARGUMENTS` and dispatch to the matching section. If no sub-mode is given, list the three options and stop.

---

### Sub-mode: `init`

Bootstrap or rebuild `garden/.voice/profile.md` from the current contents of `garden/.voice/corpus/`. Idempotent — safe to re-run after the user adds new samples.

#### Step 1 — Inventory the corpus

1. List `garden/.voice/corpus/*.md` (excluding `README.md`).
2. If fewer than 3 sample files exist, stop and tell the user the corpus is too thin for cross-author signal — a feature must appear in ≥3 sources to enter the baseline.
3. For each sample, parse the YAML frontmatter (`url`, `author`, `language`, `why`) and the prose body.
4. Report: number of samples, FR / EN counts, total word count.

#### Step 2 — Extract constraints, not phrases

For each sample compute, from the prose body only:

- **Numeric targets**: average sentence length (words), median paragraph length (sentences), citation density per 1000 words (count of `(...)` parenthetical refs and footnote markers), question rate (questions per 100 sentences).
- **Structural moves**: identify recurring devices — section headings, footnote use, blockquotes-as-digression, parenthetical asides, opening hooks (anecdote vs. claim vs. question), closing moves (summary vs. open question vs. provocation).
- **Bans (negative space)**: hedging verbs and qualifiers ("perhaps", "il semble que", "arguably", "somewhat"), tricolons, em-dash glut (>1 per 200 words), LLM-isms ("delve", "navigate the complexities"), performative qualifiers.

**Do not extract phrases, signature words, or sentence templates.** The baseline inherits *measurable scaffolding* and *negation*, never positive imitation.

#### Step 3 — Cross-author check

For each candidate feature (numeric range, structural move, ban):

- Count how many of the corpus samples exhibit it.
- **Threshold:** feature enters the baseline only if it appears in ≥3 samples (or in **all** samples when the corpus has 3 or 4 entries, i.e. the strict ≥3 rule applies regardless of corpus size).
- Features below threshold are logged separately as `single-author influence: [feature] (seen in [author])` and excluded from the baseline. The user can promote them later via `/voice mentor`.

For numeric targets: the baseline range is the median ±20% across samples that exhibit the feature.

#### Step 4 — Cole interview (positive rules)

Constraints alone don't define a voice. Conduct an 8–12 question interview to elicit positive rules. Ask questions like:

- "Pick one paragraph from [sample X] that felt right to read. What about it would you not write yourself?"
- "Which sentence in [sample Y] would you delete? Why?"
- "When you write in FR vs EN, what shifts — register, sentence length, source-citation style?"
- "Name one rhetorical move you want to use deliberately."

Record each answer as a single-line rule, tagged `[provisional]`, into the **Positive rules** section of the profile.

#### Step 5 — Write the profile

Write or overwrite `garden/.voice/profile.md` using this schema:

```markdown
---
language_modes: [fr, en]
maturity: bootstrap
last_updated: YYYY-MM-DD
decisions_count: 0
corpus_samples: N
corpus_threshold: 3
---

## Core voice (provisional)
- 3–5 adjectives synthesised from the interview answers

## Numeric targets (median ±20%)
- Avg sentence length: __ words
- Paragraph length: __ sentences
- Citation density: __ per 1000 words
- Question rate: __ per 100 sentences

## Structural moves (named, with source attribution)
- [Move] — observed in [authors]

## Bans (negative space)
- [Ban] — observed in [N/N samples]

## Positive rules (Cole interview output)
- [Rule] — [provisional] — decision id #—

## Per-language overrides
### FR
- (empty until per-language signal sediments)
### EN
- (empty until per-language signal sediments)

## Excluded — single-author influence
- [Feature] — observed in [author] only
```

#### Step 6 — Report

Print a summary: how many features entered the baseline, how many were excluded as single-author, the numeric ranges, and one line: `"Profile written at maturity: bootstrap. Re-run /voice init after adding samples to garden/.voice/corpus/."`

---

### Sub-mode: `edit <path>`

Review a single writing note against the profile. Read-only on the draft — output goes to a separate review file.

#### Step 1 — Resolve inputs

1. If `<path>` is missing, stop and ask for one.
2. Read `garden/.voice/profile.md`. If it does not exist, stop and tell the user to run `/voice init` first.
3. Read the draft at `<path>`. Parse its `date:` frontmatter to derive a review filename.

#### Step 2 — Run the checks

Each check produces a list of issues with line numbers (when locatable):

1. **Grammar and syntax** — including FR/EN code-switching errors, agreement, punctuation.
2. **Hedging hits** — match against the `Bans` section of the profile, list each occurrence.
3. **Numeric drift** — compute the same metrics as in `/voice init` Step 2, compare to the profile's `Numeric targets`, flag any metric outside the target range.
4. **Structural fidelity** — does the draft use any of the `Structural moves` named in the profile? List moves used and moves absent (informational, not a deduction).
5. **Profile-fit score (0–100)** — start at 100, deduct:
   - −3 per hedging hit (cap −15)
   - −5 per numeric metric outside range (cap −20)
   - −2 per grammar/syntax error (cap −20)
   - −10 if zero structural moves are used
   - −5 per ban hit on a `Positive rule` violation (cap −15)

#### Step 3 — Write the review

Compute the review path: `garden/notes/.review/<draft-date>-N.md` where `N` is `1` if no review exists for this draft, else `existing_count + 1`. Create `garden/notes/.review/` if it does not exist.

Review file structure:

```markdown
---
draft: <path>
draft_date: YYYY-MM-DD
review_date: YYYY-MM-DD
profile_maturity: bootstrap | sedimenting | stable
profile_fit: NN/100
---

## Profile-fit score: NN/100
[breakdown of deductions]

## Grammar and syntax
- [line N] — [issue] — [suggested fix]

## Hedging hits (vs. Bans)
- [line N] — "[hedge phrase]" — suggested deletion or replacement

## Numeric drift
- [metric]: draft = X, target = [Y, Z] — [direction of drift]

## Structural fidelity
- Used: [moves]
- Absent: [moves] (informational)

## Suggestions (≤ 5)
- [actionable rewrite suggestion]
```

#### Step 4 — Report

Print: review file path, profile-fit score, count of hedging hits, count of grammar issues, and one line: `"Run /voice mentor next to log decisions about this draft."`

Do NOT modify the draft. The review is read-only on inputs.

---

### Sub-mode: `study`

Mine the sources the garden already cites for **candidate** rules. Observes only — it asks no questions and never writes to `profile.md`. Its output is the question stock that `/voice mentor` draws on.

The premise: what is worth learning is not in the sources, it is in **what the user marked in them**. Zotero highlights are a self-selected sample of sentences the user thought worth keeping, accumulated over years of reading. That is a better voice signal than the source prose — and it costs no full-text ingestion.

#### Step 0 — The rule that governs this sub-mode

**Citation is not admiration.** Most of what the garden cites is political-science journal prose, whose habits the profile explicitly *bans* (formulaic transitions, hedging chains, unanchored abstraction). Therefore:

- Source prose **never** sets a numeric target and **never** enters `Positive rules`.
- Only the user's *selection* from a source counts, and only as a candidate that must survive elicitation in `mentor` before it sediments.
- The sole exception is an author already present in `garden/.voice/corpus/` — corpus overlap makes that author's prose legitimate style signal (e.g. Charbonnier is both cited and admired).

#### Step 1 — Resolve scope

1. Read `garden/.voice/candidates.md`. If it does not exist, this is the **first run**: scope is *every* `@citekey` appearing in `garden/notes/*.qmd`.
2. Otherwise scope is citekeys appearing in notes created or modified since the `last_run` date in the candidates frontmatter, **plus** any citekey never yet studied (tracked in the `studied:` list).
3. Report the scope before doing any work: number of notes, number of distinct citekeys, how many are new.

#### Step 1b — Run the extractor, do not hand-roll the extraction

```bash
python .claude/skills/voice/extract_highlights.py          # all citekeys in garden/notes/*.qmd
python .claude/skills/voice/extract_highlights.py aklin2020 hale2020   # or a subset
```

It reads `~/Zotero/zotero.sqlite` directly (`ZOTERO_DATA_DIR` overrides), the same way `_pre-render.py` reads tags, and writes `voice_highlights.jsonl` beside itself plus a summary to stdout.

**Do not extract via per-item MCP calls.** A single item's notes can exceed 120K characters, four distinct highlight formats coexist, and `zotero_get_annotations` silently misses annotations on secondary attachments — Run 1 lost 68% of the available signal that way. Steps 2–5 below describe what the extractor does; read them to interpret its output, not to reimplement it.

#### Step 2 — Resolve citekeys to Zotero items

For each citekey, call `zotero_search_by_citation_key` to get the item key. Record misses without failing — a citekey that no longer resolves usually means the key was regenerated after an author edit (a known hazard in this repo).

#### Step 3 — Pull and bucket highlights from **both** stores

Highlights live in two places. A run that reads only the first will silently mis-tier every source read away from the screen. Read both.

**Store 1 — attachment annotations.** Call `zotero_get_annotations` with the item key. Covers anything read *inside Zotero* and highlighted there — academic PDFs, and EPUBs, which annotate the same way.

An EPUB attachment does **not** imply annotations. Books are often read on an e-reader instead, leaving the EPUB in the library untouched while the highlights arrive by another route. Never infer "unread" or "unmarked" from an empty annotation set — check the other stores before tiering.

**Store 2 — note spans.** Call `zotero_get_notes` with `raw_html=True`. Passages transcribed while reading in print are stored as `<span style="background-color: rgba(R, G, B, 0.5)">` inside a child note, carrying the same colour code. Print-read books and FR sources live almost entirely here.

**Store 3 — e-reader exports, pasted into a Zotero note.** Highlights made on an e-reader and pasted in as plain text. Same location as store 2, different shape: **no colour survives the export.**

A store-3 note is recognised **only** by an explicit sentinel — its first line must be exactly `Highlights export`. Nothing else qualifies.

This is deliberately rigid, and the rigidity is the point. Zotero notes also hold the user's *own* commentary, written in the user's own words. If a heuristic ever mistook one of those for a source export, the pool would be contaminated with the user's existing prose and every subsequent candidate would be circular — the profile confirming what it already assumed. There is no heuristic safe enough for that failure. A note without the sentinel is never read as highlights, however much it looks like them.

Consequences of the lost colour, both of which must be honoured:

- Store-3 highlights enter the **style pool** on the 8-word floor alone. The floor already removes most of what orange and green would have caught (concept fragments, bare citation marks), so the loss is tolerable for sentence metrics.
- Store-3 highlights are **excluded from the anchoring measure**. Blue density is the anchoring signal, and an uncoloured pool has no blue. Compute anchoring over stores 1 and 2 only, and say so when reporting — an anchoring figure computed across a mixed pool would be silently wrong.

Classify every child note before reading it. Four kinds, only two of which are signal:

| Note shape | Store | Action |
|---|---|---|
| Contains `background-color: rgba(` spans | 2 | Read the spans, keep colours |
| First line is exactly `Highlights export` | 3 | Read as uncoloured highlights, one per block |
| A `data-citation-items` div | — | Ignore (Zotero citation export) |
| Anything else — TOC, publisher blurb, the user's own commentary | — | **Ignore.** Never read as highlights |

Bucket by colour, matching hex and `rgba()` equivalently — **this taxonomy is user-confirmed**:

| Colour | Hex | rgba | Meaning | Use in this sub-mode |
|--------|-----|------|---------|----------------------|
| Yellow | `#ffd400` | `255, 212, 0` | full-sentence claim | **the style signal** — pooled for metrics |
| Purple | `#a28ae5` | `162, 138, 229` | thesis statement | pooled with yellow; also marks how an author states a thesis |
| Blue | `#2ea8e5` | `46, 168, 229` | **number / empirical fact** | pooled when ≥8 words, **and** is the direct measure for the anchoring axis — blue density is how much the writer's attention goes to figures |
| Orange | `#f19837` | `241, 152, 55` | concept / vocabulary | lexical field only; never a style signal |
| Green | `#5fb236` | `95, 178, 54` | citation to chase | ignored here — bibliographic, not stylistic |

Any colour outside this table is counted and reported separately, never pooled, until the user assigns it a meaning.

Skip `image` annotations entirely. Discard yellow, purple, and blue entries shorter than 8 words — those are vocabulary or bare figures marked in a sentence colour, not sentences.

Report the two stores separately in Step 8. **A source with note-span highlights but no attachment annotations is Tier B, not Tier C** — the signal is there, it was typed rather than clicked.

#### Step 4 — Split FR / EN

Detect the language of each retained highlight from its own text, not from the parent item's metadata (a FR source may quote EN, and vice versa). Keep two separate pools. **Never pool across languages** — the profile carries genuinely different numeric targets per language (FR 24–36 words, EN 15–23), and mixing them would produce a meaningless median.

If either pool has fewer than 10 highlights, report it as too thin and emit no numeric candidate for that language. Structural and ban candidates may still be emitted.

#### Step 5 — Extract candidates

Over the yellow + purple pools, per language, compute the same measures as `init` Step 2 — average sentence length, hedge presence, anchoring (does the sentence carry a figure, date, or named actor), and opener shape (claim-first vs. build-to-claim).

Each candidate is a **proposed axis to test**, not a rule. Express it as a question `mentor` could ask, and record the evidence behind it.

#### Step 6 — Tier the sources

Every studied source gets a tier, and the tier is stated honestly rather than glossed:

| Tier | Condition | What may be learned |
|------|-----------|--------------------|
| **A** | Author also present in `garden/.voice/corpus/` | Style signal legitimate — prose and selection both |
| **B** | Has highlights in **any** of the three stores | Selection signal only — what the user marked, not how the author writes |
| **C** | No highlights in any store | **Nothing stylistic.** Record the source as unstudied and say so — do not invent a signal |

Tier C means *all three stores came back empty*, not that `zotero_get_annotations` did. Filing a print-read book as Tier C because it has no clicked annotations is the characteristic failure of this sub-mode — it silently discards the FR and book half of the library.

#### Step 7 — Append to `candidates.md`

`garden/.voice/candidates.md` is **append-only**. Create it if missing. Never rewrite or delete prior entries — a candidate that was rejected in `mentor` stays on the page marked `[rejected]` so it does not resurface as a fresh idea three months later.

```markdown
---
last_run: YYYY-MM-DD
runs: N
studied: [citekey, citekey, ...]
---

## Run N — YYYY-MM-DD

**Scope:** N notes, N citekeys (N new) · Tier A: N · Tier B: N · Tier C: N (unstudied)

### Candidates — FR
- **[axis]** — [proposed question] — evidence: N/N highlights, sources: [citekeys] — `[open]`

### Candidates — EN
- **[axis]** — [proposed question] — evidence: N/N highlights, sources: [citekeys] — `[open]`

### Unstudied (Tier C — no annotations)
- [citekey] — [title]
```

Candidate status is one of `[open]` (never asked), `[asked]` (surfaced in mentor, no verdict yet), `[confirmed]`, `[rejected]`. Only `mentor` changes a status; `study` only ever writes `[open]`.

> **Under test:** append-only is provisional. If the file becomes noisy enough to be unreadable after a few runs, the alternative is regenerating it each run and keeping only a `[rejected]` tombstone list. Revisit after run 3.

#### Step 8 — Report

Print: notes scanned, citekeys resolved / missed, highlights retrieved **broken down by store**, FR / EN pool sizes, count of new candidates by language, tier breakdown, any unmapped colours seen, and one line: `"Candidates appended. Run /voice mentor to test them against your next draft."`

State the anchoring measure's base separately (stores 1–2 only), so a reader can see it was not computed over the uncoloured store.

Do NOT write to `profile.md`. Do NOT ask questions. Both belong to `mentor`.

---

### Sub-mode: `mentor`

Iterative voice refinement through targeted questioning and threshold-gated profile updates.

#### Step 1 — Find the most recent draft and review

1. Glob `garden/notes/*.qmd`, find the most recent by `date:` frontmatter (tie-break by filename suffix).
2. Glob `garden/notes/.review/<that-date>-*.md`, read the most recent review.
3. Read `garden/.voice/profile.md` and `garden/.voice/decisions.md` (create the latter empty if missing).
4. Read `garden/.voice/candidates.md` if it exists, and collect every candidate still marked `[open]` whose language matches the draft. These seed the forced-choice questions in Step 2.
5. If no draft or no review exists, stop and tell the user to run `/voice edit` first.

#### Step 2 — Ask 2–3 targeted questions

Generate 2–3 questions that are **tied to this specific draft and review** — never abstract. Two formats are available; mix them freely.

**Format A — direct question.** Templates:

- "This paragraph used [N] hedges flagged by the profile (`[exact phrase]` on line [L]). Is `[phrase]` a stable preference of yours, or accept the deletion?"
- "The draft's average sentence length is [X] words; profile target is [Y, Z]. Was the longer/shorter rhythm deliberate here?"
- "You used [structural move] in this draft but it isn't in the profile yet. Add as a positive rule, or one-off?"
- "The profile has `[provisional rule]` at [N/3] confirmations. This draft [does/does not] follow it — count this draft as a confirmation?"

**Format B — forced choice.** Take one of the user's **own sentences** from the draft and present 2–3 rewrites of it. Prefer sentences that bear on an `[open]` candidate from `candidates.md`; fall back to a profile axis if there are none.

Three rules make this safe, and none of them are optional:

1. **One axis per pair.** Every alternative must differ from the original along exactly **one** named axis — hedged/direct, figure-anchored/abstract, in-text-attributed/`[@citekey]`, front-loaded/build-to-claim, long-multiclause/short. If two things vary at once the answer is uninterpretable.
2. **The axis sediments, never the wording.** What enters `decisions.md` is *"prefers direct over hedged in EN"*, never the sentence itself. This preserves the skill's founding constraint — the profile inherits measurable scaffolding and negation, never positive imitation. An alternative that imitates a *source's* phrasing is a bug, not a feature: it would teach pastiche.
3. **Guard against acquiescence.** The user will otherwise pick whichever alternative reads more fluently rather than the one they actually prefer. So: randomise the order of alternatives, **always** offer *"neither — keep my original"* as an option, and **reveal the axis only after the choice is made**, never in the question text.

Use AskUserQuestion to collect answers, in both formats. Each answer must be tagged with one of:

- `ban-confirm` (keep ban)
- `ban-reject` (remove ban from profile)
- `rule-add` (new positive rule, enters as `[provisional]`)
- `rule-confirm` (existing provisional rule, +1 confirmation)
- `rule-reject` (drop a provisional rule)
- `target-adjust` (numeric target needs to shift)
- `move-add` (new structural move)

#### Step 3 — Append decisions

Append one line per answer to `garden/.voice/decisions.md` (create with `# Decisions log` header if missing):

```
YYYY-MM-DD | <draft-filename> | <tag> | <item> | <candidate-id or —> | <user verbatim answer>
```

For a Format B answer, `<item>` is the **axis**, not the sentence, and `<candidate-id>` links back to the seeding entry in `candidates.md` (`—` when the question came from the profile rather than a candidate).

Decisions are append-only. They are the source of truth; the profile is a derived view.

#### Step 4 — Sedimentation rule

After appending, recompute the profile from `decisions.md`:

1. Group decisions by `(tag, item)` pair.
2. **Promotion threshold:** any `(tag, item)` group with **≥3 confirming decisions** (`rule-confirm`, `ban-confirm`, `move-add`, etc.) and **no rejecting decisions in the most recent 3** is promoted.
3. **Promotion effects:**
   - `rule-confirm` × 3 → strip `[provisional]` from the rule in the profile.
   - `ban-reject` × 3 → remove the ban from the profile (move to "Excluded — user override" section, with first decision date).
   - `target-adjust` × 3 with consistent direction → shift the numeric target by the median of suggested values.
   - `move-add` × 3 → add the structural move to the profile baseline.
4. Increment `decisions_count` in profile frontmatter by the number of *new* decisions logged this run (not the cumulative total of confirmations).
5. **Maturity gate:** count promoted-from-provisional rules in the profile.
   - `< 15` confirmed rules → `maturity: bootstrap`
   - `15–49` → `maturity: sedimenting`
   - `≥ 50` → `maturity: stable`
6. Update `last_updated: YYYY-MM-DD` in profile frontmatter.

A single decision **never** edits the profile. It sits in the log until two more confirmations arrive. This is the "sedimentation" mechanic — a counter, not a metaphor.

#### Step 5 — Update candidate statuses

For every candidate that seeded a question this run, edit its status in `garden/.voice/candidates.md` **in place** — `[open]` → `[asked]`, then `[confirmed]` or `[rejected]` once it reaches ±3 converging decisions.

Never delete a candidate line. A `[rejected]` candidate must stay visible so a later `/voice study` run does not re-propose it as a fresh idea. This is the one place any sub-mode other than `study` writes to `candidates.md`, and it may only change the status token — never the axis, evidence, or sources.

#### Step 6 — Report

Print:
- Number of decisions appended
- Any promotions that occurred (e.g., `"Promoted: ban on 'arguably' — 3/3 confirmations"`)
- Candidate status changes (e.g., `"Candidate #4 [open] → [asked]"`)
- Current maturity and `decisions_count`
- One line: `"Profile updated. Run /voice mentor again after the next draft."`

---

## Output locations

| File | Purpose | Write mode |
|------|---------|------------|
| `garden/.voice/profile.md` | Living voice profile (derived from decisions log) | overwrite on init / mentor promotion |
| `garden/.voice/corpus/*.md` | User-supplied admired-writer samples | user-managed; init reads only |
| `garden/.voice/decisions.md` | Append-only decisions log — source of truth | append on mentor |
| `garden/.voice/candidates.md` | Append-only candidate ledger from Zotero highlights | append on study; status-only edits on mentor |
| `garden/notes/.review/YYYY-MM-DD-N.md` | Per-draft review file | create on edit |

## Companion behaviour

- `/voice init` is re-runnable. Adding new samples to `garden/.voice/corpus/` and re-running rebuilds the baseline; previously-excluded `single-author influence` features may cross the ≥3 threshold and enter the baseline. The decisions log and any promoted rules are preserved — `init` only rewrites the *baseline* sections, not the `Positive rules` accumulated via `/voice mentor`.
- `/voice edit` never modifies the draft. All output goes to a separate review file.
- `/voice study` is a checkpoint activity, not a per-note one — run it when citations have accumulated, not after every draft. It is deliberately **not** wired to a `/publish` hook: a note is frozen by the time it publishes, publishing happens in batches, and a prompt that fires on every publish gets ignored within a month. `/done` suggests it passively instead.
- `/voice mentor` is the only sub-mode that mutates the profile, and only via the ≥3-confirmation rule. It reads `candidates.md` for question material and may change candidate *statuses*, nothing else.

**Order of operations:** write → `/voice edit <path>` → `/voice mentor`. `/voice study` sits outside that loop and feeds `mentor` from the side, whenever new citations have piled up.

## Important

- Profile, corpus, candidates, decisions, and reviews are all gitignored (see `.gitignore`). Treat the corpus as private — pasted full-text samples may be copyright-sensitive. Highlight text pulled by `/voice study` is quoted source material and carries the same constraint: it may sit in `candidates.md`, never in the profile and never in a commit.
- Never copy phrases, signature words, or sentence templates from corpus samples **or from Zotero highlights** into the profile. Constraints and bans only. In `mentor` Format B this means the *axis* sediments, never the wording.
- **Citation is not admiration.** A work the garden cites is not thereby a work whose prose is worth inheriting — most of it is journal prose the profile bans. `/voice study` learns from the user's *selection* within a source, not from the source.
- The threshold for cross-author signal is **strict ≥3**, not "majority". This holds even with a 4-sample corpus (3 of 4 = 75%); it is *intended* to be tight during bootstrap.
- The sedimentation threshold (`≥3 converging decisions`) is the most opinionated design choice in this skill — it exists to prevent ad-hoc profile drift.
