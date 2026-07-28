# Plan — Voice Development Workflow for `garden/notes/`

**Status:** DRAFT
**Date:** 2026-05-08
**Project:** `C:\Users\pauvernu\Documents\website\`

---

## Context

The `garden/` was created in part to build a regular writing practice and develop a personal voice. There is currently 1 writing note (`garden/notes/2026-04-17.qmd`, FR-dominant, ~2,800 words, citation-heavy essay). No editorial loop exists, and no voice profile has been articulated.

This plan introduces a `/voice` skill with three sub-modes (`init`, `edit`, `mentor`) backed by a living profile file. It addresses the no-samples-yet constraint by combining a constraint-extraction protocol on admired writers (negative space) with Cole-style interview elicitation (positive rules) — avoiding pastiche by design.

Research informing the design:
- **dropbars.be** — ban-list-heavy SKILL.md (~80% of file), 3-pass extraction
- **jordanlyall/writing-voice-skill** — manual placeholders, no corpus required
- **aaddrick/written-voice-replication** — numeric stylometric targets
- **Nicolas Cole (fiction cowork)** — interview-driven articulation when corpus is unavailable

---

## 1. Architecture decision: Skill (not subagent)

**Choice:** A single skill `.claude/skills/voice/SKILL.md` with sub-modes `init | edit | mentor`.

**Trade-off that decided it:** Subagents in this repo are reserved for *adversarial pairing* (creator vs. critic, where blind context is the point). Voice work is not adversarial — the editor must *know* the profile to score fit, not be blind to it. A skill keeps the profile, the draft, and the decision log in one context. The cost is no parallelism, which is irrelevant for solo iterative writing.

## 2. Voice profile schema

File: `garden/.voice/profile.md` (gitignored — see Open Questions).

```markdown
---
language_modes: [fr, en]
maturity: bootstrap | sedimenting | stable
last_updated: YYYY-MM-DD
decisions_count: 0
---

## Core voice (provisional)
- 3–5 adjectives (e.g., "discursive, footnoted, hesitant-precise")

## Numeric targets (from corpus, ±20%)
- Avg sentence length: __ words
- Paragraph length: __ sentences
- Citation density: __ per 1000 words
- Footnote ratio: __ per essay

## Structural moves (borrowed and named)
- Blockquote → digression footnote (cf. existing 2026-04-17 note)
- "En attente sur le métier à tisser" pending section as closer
- Subsection on a single source

## Bans (negative space — extracted from admired writers + my own rejections)
- Hedging verbs: "il semble que", "perhaps", "arguably"
- LLM-isms: tricolons, "delve", em-dash glut
- Performative qualifiers

## Positive rules (Cole interview output — sediments slowly)
- [Rule] — [decision id #N → #M agreement]

## Per-language overrides
### FR
- Specific bans / rhythms
### EN
- Specific bans / rhythms
```

## 3. Corpus bootstrap protocol (no own samples yet)

Inputs: 5–10 admired blog posts in `garden/.voice/corpus/{slug}.md` (URL + author + pasted text).

`/voice init` runs:
1. **Extract constraints, not phrases.** From each sample: numeric targets (sentence length, rhythm, citation density), structural moves, recurring negative-space bans. Phrases and signature words are explicitly *not* copied.
2. **Cole interview** — 8–12 questions: "What in this sample felt right but you would not write yourself? What sentence would you delete?" Outputs go into `Positive rules` as `[provisional]`.
3. **Cross-author check** — flag any feature that appears in fewer than 3 samples as "single-author influence" and exclude from the profile baseline.
4. Profile saved with `maturity: bootstrap`.

This addresses the pastiche risk by making the bootstrap inherit *measurable scaffolding* (numbers, structure) plus *negation* (bans), never positive phrasing.

## 4. Editor mode

Trigger: `/voice edit garden/notes/<path>.qmd` (manual; can be wired to post-`/new-note` later).

Checks (read-only inputs, writes review file):
- Grammar, syntax, FR/EN switching
- Hedging hits against `Bans`
- Numeric drift from targets (sentence length, paragraph rhythm)
- Structural fidelity (does it use the named moves?)
- Profile-fit score 0–100 with deductions

Output: `garden/notes/.review/YYYY-MM-DD-N.md` — separate file, not inline annotations, so the draft stays clean and the review is greppable.

## 5. Mentor mode and sedimentation loop

Trigger: `/voice mentor` after a draft (or every 3rd note).

Loop:
1. Reads the most recent note + last review.
2. Asks **2–3 targeted questions** tied to that draft only — not abstract ("This paragraph used 4 hedges. Keep, or is this a stable preference?").
3. Appends each answer as one line to `garden/.voice/decisions.md` with date, draft id, and tag (`ban-confirm`, `ban-reject`, `rule-add`, `target-adjust`).
4. **Sedimentation rule:** profile updates only when ≥3 decisions in `decisions.md` converge on the same tag for the same item. Single decisions never edit the profile — they sit in the log. At 3 confirmations, the rule is promoted from `[provisional]` to active; `decisions_count` increments; `maturity` advances `bootstrap → sedimenting → stable` at 15 / 50 confirmed rules.

This makes "sedimentation" a counter, not a metaphor.

## 6. First three concrete steps (this week)

1. **Scaffold the skill** — create `.claude/skills/voice/SKILL.md` with frontmatter (`name: voice`, `argument-hint: "init | edit <path> | mentor"`, `allowed-tools: [Read, Write, Edit, Glob, Grep]`), and the three sub-mode procedural blocks. Mirror `done/SKILL.md` structure.
2. **Seed the corpus** — create `garden/.voice/corpus/` and drop 5–10 admired blog posts in plain markdown with URL + author header. Add `garden/.voice/` to `.gitignore`.
3. **Run `/voice init`** — bootstrap `profile.md`, then write a fresh note and run `/voice edit` followed by `/voice mentor` to test the full loop end-to-end.

---

## Critical files

| File | Action | Reuses |
|------|--------|--------|
| `.claude/skills/voice/SKILL.md` | Create | Skill structure from `.claude/skills/done/SKILL.md`, `.claude/skills/new-note/SKILL.md`; `@.claude/rules/` reference pattern from `prompt-refine` |
| `garden/.voice/profile.md` | Create on `/voice init` | n/a |
| `garden/.voice/corpus/*.md` | User-supplied | n/a |
| `garden/.voice/decisions.md` | Append on `/voice mentor` | Append-only pattern from `.claude/session-log.md` |
| `garden/notes/.review/*.md` | Create on `/voice edit` | Review-file pattern from archived `proofread` skill |
| `.gitignore` | Add `garden/.voice/` and `garden/notes/.review/` | n/a |

## Verification (end-to-end test)

1. Create `garden/.voice/corpus/` with 5+ sample blog posts.
2. Run `/voice init` → confirm `profile.md` exists with bootstrap fields populated, all positive rules tagged `[provisional]`.
3. Write a new note via `/new-note` and run `/voice edit garden/notes/<file>.qmd` → confirm review file created at `.review/`, profile-fit score present, hedging flagged.
4. Run `/voice mentor` → confirm 2–3 questions ask about the specific draft, answers append to `decisions.md`, profile is unchanged (no 3-of-a-kind yet).
5. Repeat steps 3–4 across 3 drafts → confirm at least one rule promotes from `[provisional]` to active in `profile.md` and `decisions_count` increments.

---

## Self-verification

**Key assumptions**
- Claude Code skills can be invoked as `/voice [submode] [args]` — confirmed by `done`, `new-note`, `prompt-refine` precedent.
- `garden/.voice/` is gitignored (confirmed with user — personal corpus, copyright-sensitive samples).
- One bilingual profile with per-language overrides (confirmed with user); revisit if FR/EN diverge once `maturity: sedimenting`.

**Verified vs. design call**
- Verified from research: ban-list dominance (dropbars), interview method (Cole), numeric targets (aaddrick), no-corpus fallback (jordanlyall), pastiche risk on positive imitation (cross-cited).
- Design call (mine, not from references): the **3-of-a-kind sedimentation threshold** — none of the surveyed implementations use a quantitative gate; they update profiles ad-hoc, which is exactly what produces drift. This is the most opinionated choice in the plan.
- Design call: **single skill with sub-modes** rather than worker-critic pair — fits this repo's separation-of-powers doctrine (voice work is non-adversarial).

**Remaining open questions (defaults will apply unless you override)**
1. **Mentor cadence** — every draft initially (during `bootstrap`), drop to every 3rd once `maturity: sedimenting`. Override if you'd prefer every-3rd from day one.
2. **Auto-trigger `/voice edit` after `/new-note`?** Default: no, manual for the first month. Auto-wiring via Quarto pre-render or a hook is a v2 concern.
3. **Corpus samples — paste full text or URLs only?** Default: paste full text (since `garden/.voice/` is gitignored, copyright is moot). URLs alone are too brittle for offline analysis.
