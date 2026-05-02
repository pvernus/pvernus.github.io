# Model Routing Framework

**Single source of truth for agent model assignments.**

Model overrides: per-invocation `--model` flag > `## Active Model Overrides` in CLAUDE.md > this table.

---

## Task-Demand Taxonomy

Agents are scored on 5 axes (1–3):

| Axis | 1 (low) | 2 (mid) | 3 (high) |
|------|---------|---------|---------|
| **A: Reasoning depth** | Checklist / pattern-match | Structured judgment | Open-ended synthesis |
| **B: Creativity / generation** | Pure evaluation | Templated generation | Freeform generation |
| **C: Error cost** | Advisory / easily caught | Blocks phase, critic catches | Compounds silently or expensive to reverse |
| **D: Output structure** | Highly templated | Semi-structured | Freeform |
| **E: Speed sensitivity** | Speed irrelevant | Called 1–2×/session | Frequent / interactive |

## Routing Heuristic

```
Sum >= 10  → Opus 4.6    (claude-opus-4-6)
Sum  7–9   → Sonnet 4.6  (claude-sonnet-4-6)
Sum <=  6  → Haiku 4.5   (claude-haiku-4-5-20251001)

Override rules (applied after sum):
  A=3 AND C=3  → floor at Opus (minimum)
  B=1 AND D=1  → cap at Sonnet (sufficient for structured checklists)
```

**Rationale:** Opus is the default for all planning and execution agents (sum ≥ 10).
Sonnet is reserved for structured critic checklists (sum 7–9). Haiku for pure PASS/FAIL.

---

## Routing Table

| Agent | A | B | C | D | E | Sum | **Model** | Key rationale |
|-------|---|---|---|---|---|-----|-----------|---------------|
| strategist | 3 | 3 | 3 | 3 | 3 | 15 | **claude-opus-4-6** | Identification errors corrupt the entire pipeline |
| coder | 2 | 3 | 3 | 3 | 3 | 14 | **claude-opus-4-6** | Subtle bugs (wrong clustering, FE spec) are expensive to catch |
| writer | 3 | 3 | 2 | 3 | 3 | 14 | **claude-opus-4-6** | Model quality difference most visible in long-form prose |
| domain-referee | 3 | 1 | 3 | 2 | 3 | 12 | **claude-opus-4-6** | Contribution judgment requires deep domain knowledge |
| methods-referee | 3 | 1 | 3 | 2 | 3 | 12 | **claude-opus-4-6** | Identification validity check at submission gate |
| strategist-critic | 3 | 1 | 3 | 2 | 3 | 12 | **claude-opus-4-6** | A=3+C=3 → Opus floor; plan validation is high-stakes |
| data-engineer | 2 | 3 | 2 | 3 | 2 | 12 | **claude-opus-4-6** | Code execution quality benefits from Opus |
| storyteller | 2 | 3 | 1 | 3 | 2 | 11 | **claude-opus-4-6** | Creative generation; Opus produces better structured narratives |
| orchestrator | 3 | 1 | 3 | 2 | 1 | 10 | **claude-opus-4-6** | Core planning agent; A=3+C=3 → Opus; plan quality justifies cost |
| librarian | 2 | 2 | 2 | 2 | 2 | 10 | **claude-opus-4-6** | Synthesis with judgment; Opus for broader coverage |
| explorer | 2 | 2 | 2 | 2 | 2 | 10 | **claude-opus-4-6** | Data assessment feeds strategy; errors compound |
| coder-critic | 2 | 1 | 3 | 1 | 3 | 10 | **claude-opus-4-6** | Code review is high-stakes; Opus catches subtle issues |
| writer-critic | 2 | 1 | 2 | 1 | 2 | 8 | **claude-sonnet-4-6** | Structured proofreading checklist; Sonnet sufficient |
| librarian-critic | 2 | 1 | 2 | 1 | 2 | 8 | **claude-sonnet-4-6** | Coverage gap checklist; Sonnet sufficient |
| explorer-critic | 2 | 1 | 2 | 1 | 2 | 8 | **claude-sonnet-4-6** | Feasibility scoring; Sonnet sufficient |
| storyteller-critic | 1 | 1 | 1 | 1 | 2 | 6 | **claude-haiku-4-5-20251001** | Advisory, mechanical checklist |
| verifier | 1 | 1 | 2 | 1 | 1 | 6 | **claude-haiku-4-5-20251001** | PASS/FAIL bash checklist |

**Distribution:** 12 Opus · 3 Sonnet · 2 Haiku

---

## Override Mechanism (precedence order, highest first)

1. **Per-invocation flag** — user passes `--model haiku|sonnet|opus` to any skill invocation
2. **Session-level override** — `## Active Model Overrides` section in `CLAUDE.md` (cleared when no longer needed)
3. **This routing table** — canonical default

The Orchestrator logs the *resolved* model for every agent dispatch in the research journal.

---

## Evaluation Protocol

**Core idea:** run the same task with two models on real project artifacts, score blind (standard 100-pt rubric), downgrade default if cheaper model >= 85/100.

### Standard rubric (100 points)

| Criterion | Points |
|-----------|--------|
| Task completion | 25 |
| Domain accuracy | 25 |
| Reasoning depth | 25 |
| Format compliance | 25 |

### Per-agent test inputs

| Agent | Test input | What to compare |
|-------|------------|-----------------|
| strategist | Research question + data assessment | ID logic, parallel trends defense, referee anticipation |
| coder | Approved strategy memo for `res_base.qmd` | fixest spec, clustering, FE choices |
| writer | Results + strategy memo | Introduction quality, anti-hedging, effect size reporting |
| strategist-critic | Draft strategy memo | Issue detection rate, severity calibration |
| domain-referee | `output/paper/draft.qmd` | Contribution assessment, literature gap detection |
| methods-referee | `output/paper/draft.qmd` | Identification checklist, inference checks |
| coder-critic | Script with 3 planted errors (critical/major/minor) | Detection rate by severity |
| verifier | `output/paper/` | PASS/FAIL accuracy |

**Decision rule:** lower-model score >= 85 → downgrade default. < 85 → document the specific failure mode in the rationale column above.

**Evaluation outputs:** `quality_reports/model-eval/[agent]_[model].md`

### When to run evaluations

- At framework introduction (validate all Opus defaults)
- After a major model release
- After 3-strikes escalation on any agent (may signal model underperformance)
- Quarterly for the 5 Opus agents (highest downgrade value if cheaper model suffices)

---

## Maintenance

When updating model assignments:
1. Update the routing table above
2. Update the affected agent's `model:` frontmatter in `.claude/agents/[agent].md`
3. Record the change and test result in `quality_reports/model-eval/`
4. Add a `[LEARN:infrastructure]` entry to `MEMORY.md`
