# Logging: Sessions, Handoff, and On-Demand Rollups

This project runs a **two-tier persistent** session system plus **on-demand** satellites. `/done` writes the persistent tiers at session end; `/start` reads them at session begin; `/tools *` produces the rollups when you ask for them. Nothing else writes session state automatically.

---

## Composition

```
              writes                       reads
  ┌──────────────────────────┐     ┌──────────────────────────┐
  │  /done (session end)     │     │  /start (session begin)  │
  └──────────────┬───────────┘     └──────────────┬───────────┘
                 │                                │
                 ▼                                ▼
  ┌──────────────────────────────────────────────────────────┐
  │  Tier 1 (append):    .claude/session-log.md              │
  │  Tier 2 (overwrite): .claude/handoff.md                  │
  └──────────────────────────────────────────────────────────┘

  On demand (called explicitly, not from /done or /start by default):
    /tools learn    → MEMORY.md + .claude/state/personal-memory.md
    /tools context  → prints context-window health (no file)
    /tools journal  → quality_reports/research_journal.md (regenerated)

  At merge time only:
    /done when session ended in a merge → quality_reports/merges/YYYY-MM-DD_<branch>.md
    using templates/quality-report.md
```

---

## 1. Tier 1 — Session Log (persistent, append)

**File:** `.claude/session-log.md` (reverse chronological, newest first)
**Writer:** `/done` (all sub-modes).
**Reader:** `/start` reads the last 1–2 entries for context; humans grep it.
**Pruning:** `/done` removes entries older than 60 days.

### Entry format

```markdown
## YYYY-MM-DD HH:MM — [Session Topic]

**Decisions:**
- [Decision made] — [rationale]

**Unresolved:**
- [Open question or deferred item]

**Next steps:**
- [ ] [Actionable follow-up]

**Files:**
- [path/to/file] — [created/modified/deleted]
```

### Rules

1. **Append only** — never rewrite past entries.
2. **Newest first** — prepend, don't append to end of file.
3. **Concise** — 5–15 lines per entry. If a session produced more, summarise; detail belongs in code and commits.
4. **Missing file is created automatically** by `/done` with header `# Session Log — [Project Name]`.

---

## 2. Tier 2 — Handoff (persistent, overwrite)

**File:** `.claude/handoff.md` (current state only)
**Writer:** `/done` (merge protocol — carry forward unfinished items).
**Reader:** `/start` reads this first and treats it as authoritative for "where we left off."

### Merge protocol (enforced by `/done`)

1. Read the existing `handoff.md`.
2. Carry forward every `- [ ]` task from **Resume here** that was not completed this session.
3. Carry forward every bullet from **Context to remember**. If a new session makes a carried entry stale, it MAY be removed — but only with an inline justification (`superseded by X`, `no longer true after commit Y`). Never silently drop.
4. Prepend new items so the most urgent ones appear first.

### Structure

```markdown
# Handoff — [Date]

**Last session:** [Topic]
**Status:** [What was completed]

**Resume here:**
- [ ] [New action — most urgent first]
- [ ] [Carried-forward unfinished tasks]

**Context to remember:**
- [New context from this session]
- [Carried-forward context — never silently deleted]
```

---

## 3. On-demand satellites — `/tools`

These are **not** written by `/done` or `/start`. They run when you invoke them.

### `/tools learn` — writes to `MEMORY.md` + `.claude/state/personal-memory.md`

Promotes `[LEARN:category]` patterns from the current session into persistent memory. `/done` passively suggests running this when it detects reusable patterns (one-line prompt at end of capture); it does not auto-invoke. The two-tier memory split (generic → `MEMORY.md`, machine-specific → `.claude/state/personal-memory.md`) is documented in `.claude/rules/meta-governance.md`.

### `/tools context` — no file, prints a report

Summarises context-window state and compaction status. `/start post-compact` invokes this as an optional step 0; default `/start` does not.

### `/tools journal` — writes to `quality_reports/research_journal.md`

Regenerates an agent-level research-history rollup from quality reports + git history. The file is **ephemeral** — it does not persist between regenerations in a meaningful way; `/done` does not maintain it. Run this when you want a chronological view of agent actions, phase transitions, scores, and escalations.

When you do regenerate it, use this per-event format:

```markdown
### YYYY-MM-DD HH:MM — [Agent Name]
**Phase:** [Discovery / Strategy / Execution / Peer Review / Presentation]
**Target:** [file or topic reviewed]
**Score:** [XX/100 or PASS/FAIL or N/A]
**Verdict:** [one line — the key finding or decision]
**Report:** [link to full report]
```

---

## 4. Merge-time quality reports

Generated **only** when the session ends in a merge to `main`. Not per commit, not per PR.

**Location:** `quality_reports/merges/YYYY-MM-DD_[branch-name].md`
**Template:** `templates/quality-report.md`
**Written by:** `/done` (merge branch only).

---

## 5. Review artifacts (separate subsystem)

`/review` and its critics produce artifacts under `quality_reports/`:

| Subfolder | Contents |
|-----------|----------|
| `quality_reports/reviews/` | `/review` outputs, referee simulations, proofreads, strategist-critic reviews, framework audits |
| `quality_reports/revisions/` | R&R trackers, response letters, referee-comment routing |
| `quality_reports/plans/` | Approved plans from plan mode (`YYYY-MM-DD_<description>.md`) |
| `quality_reports/specs/` | Requirements specs (`templates/requirements-spec.md` instances) |
| `quality_reports/merges/` | Merge-time quality reports (see §4) |
| `quality_reports/archive/` | Retired documents preserved for history |

`/done` does **not** touch these. They are written by the skills that produce them (`/review`, `/revise`, `/strategize`, etc.) and read by humans or by targeted skills that need prior review context.

---

## 6. What changed vs. the old spec

The previous version of this file specified three persistent tiers (`session_logs/`, `SESSION_REPORT.md`, `research_journal.md`) and a mirror (`.claude/SESSION_REPORT.md`). In practice:

- `quality_reports/session_logs/` was never populated by any skill — **retired**.
- `SESSION_REPORT.md` and its `.claude/` mirror duplicated each other and overlapped with `.claude/session-log.md` — **archived to `quality_reports/archive/session_report_2026-03-to-04.md`**.
- `research_journal.md` was never created as a persistent log — **redefined** as an on-demand `/tools journal` output.

The current two-tier + satellites model matches what `/done` actually does, which is what matters.
