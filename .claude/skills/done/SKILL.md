# Session Capture — Complete Documentation

*v1.2 — Document work sessions for cross-session continuity*

## Input
$ARGUMENTS

## Instructions

Session Capture documents work sessions for cross-session continuity.

### Core workflow (6 steps)

**Step 1: Identify scope**
Review the conversation history for:
- Topic and project name
- Session length: Brief (< 30 min), Medium (30–90 min), Extended (> 90 min)
- Key themes and outputs

**Step 2: Extract artifacts**
Identify:
- Decisions made (design choices, direction changes, resolved questions)
- Unresolved questions (open items, ambiguities, deferred choices)
- Concrete next steps / follow-ups (actionable items for the next session)
- Files created or modified (with paths)

**Step 3: Write session entry**
Append to `.claude/session-log.md` in reverse chronological order (newest first):

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

Create `.claude/session-log.md` with a title header if it doesn't exist:
`# Session Log — [Project Name]`

**Step 4: Generate handoff note**
Update `.claude/handoff.md` using the following merge protocol:

1. **Read the existing `handoff.md`** (if it exists).
2. **Carry forward all unfinished tasks** from the prior **Resume here:** section — do not delete any `- [ ]` items that have not been explicitly completed this session.
3. **Carry forward all bullets** from the prior **Context to remember:** section. If new session context makes a carried-forward entry stale, outdated, or superseded, you MAY propose removing or updating it — but you MUST include an inline justification explaining why (e.g., "superseded by X", "no longer true after commit Y"). Never silently drop entries.
4. **Prepend new items** from the current session at the top of each section so the most urgent items appear first.
5. Write the updated file with this structure:

```markdown
# Handoff — [Date]

**Last session:** [Topic]
**Status:** [What was completed]

**Resume here:**
- [ ] [New action from this session — most urgent first]
- [ ] [Carried-forward unfinished tasks from previous sessions]

**Context to remember:**
- [New context from this session]
- [Carried-forward context from previous sessions — never deleted]
```

**Step 5: Maintenance**
- Prune entries from `.claude/session-log.md` older than 60 days
- Confirm output locations: `.claude/session-log.md` and `.claude/handoff.md`
- If the session ended in a merge to `main`, also append a merge-time report to `quality_reports/merges/YYYY-MM-DD_<branch>.md` using `templates/quality-report.md`.

**Step 6: Suggest `/tools learn` (passive — do not auto-invoke)**

Scan the session for patterns worth promoting to persistent memory:
- Novel workarounds or corrections (especially those the user flagged with `[LEARN:...]`)
- Reusable multi-step workflows that would save future-Claude time
- Non-obvious setup quirks (machine-specific → `.claude/state/personal-memory.md`; generic → `MEMORY.md`)

If any qualify, print one line at the end:

> *Consider running `/tools learn` to capture: [1-line summary of the candidate learnings]*

If nothing qualifies, say nothing. `/done` never writes to `MEMORY.md` itself — that is `/tools learn`'s job. Keeping this step passive prevents low-signal pollution of shared memory.

**Step 7: Suggest `/voice study` (passive — do not auto-invoke)**

If the session added or modified any `garden/notes/*.qmd`, compare the `@citekey`s they cite against the `studied:` list in `garden/.voice/candidates.md` (skip this step silently if that file does not exist and no note was touched).

If unstudied citekeys exist, print one line at the end:

> *Consider running `/voice study` — N cited source(s) not yet mined for voice candidates: [citekeys]*

Passive by design. `/voice study` is a checkpoint activity that rewards batching — the ≥3-confirmation sedimentation rule needs a volume of decisions, and volume comes from sweeping several sources at once rather than one per session.

---

### Argument modifiers

- `quick` — abbreviated capture: decisions and follow-ups only (skip detailed file list)
- `project:name` — tag entry to a specific project name

---

### Output locations

| File | Purpose | Write mode |
|------|---------|------------|
| `.claude/session-log.md` | Reverse-chronological session history | append (newest first) |
| `.claude/handoff.md` | Most recent session context for next-session resumption | overwrite (with carry-forward merge) |
| `quality_reports/merges/YYYY-MM-DD_<branch>.md` | Merge-time quality report (only if session ended in a merge) | create |

### Companion skills

| Skill | When to use | Relationship |
|-------|-------------|--------------|
| `/start` | Next session | Reads `.claude/handoff.md` and the top of `.claude/session-log.md`. |
| `/tools learn` | When `/done` suggests it | Promotes session patterns to `MEMORY.md` + `.claude/state/personal-memory.md`. |
| `/tools journal` | On demand | Regenerates `quality_reports/research_journal.md` from quality reports + git history. Not maintained by `/done`. |

---

### Important
- Missing log files are created automatically with proper headers
- The handoff file overwrites the previous session's notes each time — only the most recent context persists
- Use `quick` for brief check-ins; full capture for substantive sessions
- `/done` never writes to `MEMORY.md`, `SESSION_REPORT.md`, `quality_reports/session_logs/`, or `quality_reports/research_journal.md` — those are either retired (`SESSION_REPORT.md`, `session_logs/`) or handled by other skills (`/tools learn`, `/tools journal`)
