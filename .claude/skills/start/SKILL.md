---
name: start
description: Session-start orientation — reads handoff, recent plan, session-log tail, DATA_CATALOG.md, data/codebook.csv, MEMORY.md, and git state; prints a short orientation. Read-only, never writes files.
disable-model-invocation: true
argument-hint: "[quick | plan:<file> | post-compact]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Session Start

*v1.0 — Read-only session orientation*

Prints a short orientation at the start of a session. Reads state, never writes it. The write side is `/done`.

## Input

`$ARGUMENTS` — optional sub-mode.

## Sub-modes

- *(none)* — full orientation (default).
- `quick` — skip step 3 (plan) and step 5 (data catalog); emit only handoff + git + recent log tail.
- `plan:<file>` — resume a specific plan file (path relative to `quality_reports/plans/` or absolute). Overrides the "most recent plan" heuristic.
- `post-compact` — prepend a one-line context-health probe from `/tools context` before the standard orientation. Use only when resuming after a compaction event.

## Core workflow (8 steps)

### Step 0 — Optional context probe (`post-compact` mode only)

Invoke `/tools context` and summarise in one line (e.g., "Context restored; handoff and plan preserved"). Skip entirely in default and `quick` modes.

### Step 1 — Handoff (authoritative "where we left off")

Read `.claude/handoff.md`.

- If missing: state *"No prior handoff — fresh start"* and skip to step 7.
- If present: extract **Last session**, **Status**, **Resume here** (every `- [ ]`), and **Context to remember** (every bullet). Carry all `Resume here` items verbatim into the orientation — they are the primary user-facing output.

### Step 2 — Recent session entries

Read the first 1–2 `## YYYY-MM-DD HH:MM — ...` entries from `.claude/session-log.md`. Extract any unresolved items or decisions worth surfacing.

Skip entries older than 14 days; they belong in the handoff or are stale.

### Step 3 — Active plan (skip in `quick` mode)

Resolve the target plan:

- If `plan:<file>` was passed: use that file.
- Otherwise: `ls -t quality_reports/plans/*.md | head -1` — the single most recent plan.

Read the plan and report: status (DRAFT / APPROVED / COMPLETED), one-line summary of the goal, and any outstanding steps.

### Step 4 — Relevant prior learnings

Read `MEMORY.md`. Scan `[LEARN:category]` entries — surface at most 3 whose category matches the handoff topic or the active plan's domain.

Do **not** dump all entries. If none match, output nothing from this step.

### Step 5 — Data context (skip in `quick` mode)

Read the first ~80 lines of `DATA_CATALOG.md` and the first ~10 rows of `data/codebook.csv`.

Summarise in ≤ 3 lines: pipeline stage, newest intermediate object, and whether the codebook references any variable mentioned in the handoff.

### Step 6 — `.claude/state/` scan (optional)

If `.claude/state/personal-memory.md` exists, scan it for any machine-specific notes (paths, tool versions, quirks) that apply to the current task. Surface at most 2.

### Step 7 — Git state

Run:

```bash
git status --short
git log --oneline -5
git branch --show-current
```

Report: current branch, count of uncommitted changes (staged/unstaged), and the 2–3 most recent commit subjects.

### Step 8 — Emit orientation

Print a ≤ 25-line block structured exactly as:

```
## Orientation — YYYY-MM-DD HH:MM on <branch>

**Where we left off** *(from .claude/handoff.md)*
- Last session: <topic>
- Status: <what was completed>
- Resume here:
  - [ ] <task 1>
  - [ ] <task 2>

**Active plan** *(from quality_reports/plans/<file>)*
- Status: <DRAFT | APPROVED | COMPLETED>
- <one-line summary and outstanding steps>

**Relevant prior learnings** *(from MEMORY.md — filtered, ≤3)*
- [LEARN:<cat>] <entry>

**Data context** *(from DATA_CATALOG.md + data/codebook.csv)*
- <one line on pipeline stage / newest artifact / codebook coverage>

**Git state**
- <branch>, <N staged / M unstaged>, latest: <hash> <subject>

**Suggested next action**
- <single sentence inferred from handoff "Resume here" + plan status>
```

Any section that resolves to nothing (e.g., no handoff, no matching learning) is omitted entirely — do not print empty headers.

## Non-outputs

- **No file writes** — `/start` is strictly read-only. Running it twice in a row produces the same output (idempotent).
- **No auto-invocation of `/done`** — session-end is user-triggered.
- **No automatic promotion to `MEMORY.md`** — use `/tools learn` for that.

## Relationship to other skills

| Skill | When | What it does | Writes? |
|-------|------|--------------|---------|
| `/start` | Session begin | Reads and orients | no |
| `/done` | Session end | Captures decisions + updates handoff | `.claude/session-log.md`, `.claude/handoff.md` |
| `/tools learn` | On demand after a session | Promotes `[LEARN:]` patterns to persistent memory | `MEMORY.md`, `.claude/state/personal-memory.md` |
| `/tools context` | Post-compact or when curious | Prints context-window health | no |
| `/tools journal` | On demand | Regenerates `quality_reports/research_journal.md` | `quality_reports/research_journal.md` |

## Rules

- Respect `.gitignore`. The files `/start` reads (`CLAUDE.md`, `.claude/*`, `MEMORY.md`, `quality_reports/*`, `templates/*`) are project-local by design.
- Never print raw file contents — always summarise. The user has limited screen-inches at session start.
- Token budget: target ≤ 25 lines of output. Truncate long handoff tasks rather than rendering them in full.
- If a file referenced by the workflow is missing, state so in one line (`no session-log yet`) and move on. Never fail.
