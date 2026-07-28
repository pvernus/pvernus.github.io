---
name: voice
description: Develop and apply a personal writing voice for garden/notes/. Three sub-modes — init (bootstrap a voice profile from a corpus of admired writers), edit (review a draft against the profile), mentor (ask draft-specific questions and sediment answers into the profile after 3 converging confirmations).
argument-hint: "init | edit <path> | mentor"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# /voice — Writing Voice Workflow

*v1.0 — Bootstrap, apply, and iteratively refine a personal writing voice for `garden/notes/`*

Three paired functions, one shared profile:

1. **`/voice init`** — bootstrap or rebuild `garden/.voice/profile.md` from `garden/.voice/corpus/` (re-runnable as corpus grows)
2. **`/voice edit <path>`** — review a draft note; write a separate review file with grammar/syntax fixes and a profile-fit score
3. **`/voice mentor`** — ask 2–3 draft-specific questions; log answers; sediment confirmed rules into the profile after **≥3 converging decisions**

Profile, corpus, and decisions live under `garden/.voice/` (gitignored). Reviews live under `garden/notes/.review/` (gitignored).

## Input

`$ARGUMENTS` — one of: `init`, `edit <path>`, `mentor`.

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

### Sub-mode: `mentor`

Iterative voice refinement through targeted questioning and threshold-gated profile updates.

#### Step 1 — Find the most recent draft and review

1. Glob `garden/notes/*.qmd`, find the most recent by `date:` frontmatter (tie-break by filename suffix).
2. Glob `garden/notes/.review/<that-date>-*.md`, read the most recent review.
3. Read `garden/.voice/profile.md` and `garden/.voice/decisions.md` (create the latter empty if missing).
4. If no draft or no review exists, stop and tell the user to run `/voice edit` first.

#### Step 2 — Ask 2–3 targeted questions

Generate 2–3 questions that are **tied to this specific draft and review** — never abstract.

Templates:

- "This paragraph used [N] hedges flagged by the profile (`[exact phrase]` on line [L]). Is `[phrase]` a stable preference of yours, or accept the deletion?"
- "The draft's average sentence length is [X] words; profile target is [Y, Z]. Was the longer/shorter rhythm deliberate here?"
- "You used [structural move] in this draft but it isn't in the profile yet. Add as a positive rule, or one-off?"
- "The profile has `[provisional rule]` at [N/3] confirmations. This draft [does/does not] follow it — count this draft as a confirmation?"

Use AskUserQuestion to collect answers. Each answer must be tagged with one of:

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
YYYY-MM-DD | <draft-filename> | <tag> | <item> | <user verbatim answer>
```

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

#### Step 5 — Report

Print:
- Number of decisions appended
- Any promotions that occurred (e.g., `"Promoted: ban on 'arguably' — 3/3 confirmations"`)
- Current maturity and `decisions_count`
- One line: `"Profile updated. Run /voice mentor again after the next draft."`

---

## Output locations

| File | Purpose | Write mode |
|------|---------|------------|
| `garden/.voice/profile.md` | Living voice profile (derived from decisions log) | overwrite on init / mentor promotion |
| `garden/.voice/corpus/*.md` | User-supplied admired-writer samples | user-managed; init reads only |
| `garden/.voice/decisions.md` | Append-only decisions log — source of truth | append on mentor |
| `garden/notes/.review/YYYY-MM-DD-N.md` | Per-draft review file | create on edit |

## Companion behaviour

- `/voice init` is re-runnable. Adding new samples to `garden/.voice/corpus/` and re-running rebuilds the baseline; previously-excluded `single-author influence` features may cross the ≥3 threshold and enter the baseline. The decisions log and any promoted rules are preserved — `init` only rewrites the *baseline* sections, not the `Positive rules` accumulated via `/voice mentor`.
- `/voice edit` never modifies the draft. All output goes to a separate review file.
- `/voice mentor` is the only sub-mode that mutates the profile, and only via the ≥3-confirmation rule.

## Important

- Profile, corpus, decisions, and reviews are all gitignored (see `.gitignore`). Treat the corpus as private — pasted full-text samples may be copyright-sensitive.
- Never copy phrases, signature words, or sentence templates from corpus samples into the profile. Constraints and bans only.
- The threshold for cross-author signal is **strict ≥3**, not "majority". This holds even with a 4-sample corpus (3 of 4 = 75%); it is *intended* to be tight during bootstrap.
- The sedimentation threshold (`≥3 converging decisions`) is the most opinionated design choice in this skill — it exists to prevent ad-hoc profile drift.
