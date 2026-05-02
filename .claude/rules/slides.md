# Slides: Rhetoric of Decks

Apply these rules whenever creating or editing `output/slides/*.qmd` or any Beamer `.tex` presentation. These are constraints, not guidelines.

---

## The Non-Negotiable Rules

### One idea per slide
If a slide has two ideas, split it. No exceptions.

### Titles are assertions, not labels

- Bad: "Results"
- Good: "Disasters increase non-state aid by X% but crowd out bilateral state flows"
- Bad: "Literature Review"
- Good: "Prior work ignores the channel composition of post-disaster aid"

Reading slide titles in sequence should communicate the entire argument.

### No bullet lists (usually)
Bullets signal you haven't found the structure. Instead:
- A **sequence** → flow diagram or numbered steps
- A **contrast** → two columns
- A **hierarchy** → size/color differentiation
- A **causal chain** → arrows

Exception: genuinely parallel items (e.g., a list of identifying assumptions).

### Typography minimums
- Body text: 24pt minimum
- Absolute floor (footnotes, source notes): 18pt
- Never justify text — ragged right only

### Charts: one message, direct labels
- Every chart communicates ONE finding
- Title states the finding, not the chart type
- Label data directly — no legends requiring eye movement
- Remove chartjunk: gridlines, borders, unnecessary axis marks

### White space is confidence
A full slide signals anxiety. Empty space signals careful selection.

### Zero compile warnings
Not "try to fix." Zero. Check with:
```bash
grep -cE "Overfull|Underfull" [file].log
```

---

## Slide Architecture

### Opening slide (first content slide)
Not "Motivation" with bullets. Instead:
- A surprising fact or statistic (big number, centered)
- A puzzle or unanswered question
- A provocative claim the deck will support

### Transition slides
Dark-background section dividers between major sections. One line title, one line subtitle.

### Closing slide
Not "Questions?" or "Thank you." Instead:
- The ONE sentence the audience should remember tomorrow
- Dark background, takeaway centered

### Devil's advocate slide (academic seminars)
Present the strongest objection, then respond. Format: "A skeptic would say… / We address this by…"

---

## Narrative Arc

Every deck: **Setup → Development → Resolution**

- **Setup**: Establish the problem. Make the audience feel it.
- **Development**: Evidence, analysis, logical case.
- **Resolution**: The insight. Implications. One thing to remember.

Apply the **Pyramid Principle**: lead with the conclusion, then support it. State the finding first, then prove it. Do not build suspense.

---

## For This Project's Slides (`phd_sem_202507.qmd`)

- Audience: PhD seminar — sparse, one idea per slide, titles carry the argument
- Key result slides: state the ATT estimate with units in the title
- Event-study plots: show pre-trends explicitly; title asserts the pre-trend result ("Pre-trends are flat; disasters shift non-state aid post-event")
- Channel decomposition: one slide per channel type, not all in one table

---

## Reference
Full philosophy: `claude_lib/MixtapeTools-main/presentations/rhetoric_of_decks.md`
Operational rules: `claude_lib/MixtapeTools-main/.claude/skills/compiledeck/SKILL.md`
