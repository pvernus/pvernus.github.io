# Domain Profile

<!--
HOW TO USE: Fill this in manually OR let /discover (interactive interview) generate it.
All agents read this file to calibrate their field-specific behavior.
Delete sections that don't apply. Add sections specific to your field.
-->

## Field

**Primary:** Development Economics, Political Economy of Aid
**Adjacent subfields:** International Relations, Public Finance, Environmental Economics (climate/disasters)

---

## Target Journals (ranked by tier)

<!-- The Orchestrator uses this for journal selection. The Librarian prioritizes these in searches. -->

| Tier | Journals |
|------|----------|
| Top-5 | AER, QJE, REStud |
| Top field | AEJ:Applied, AEJ:Policy, JDE (Journal of Development Economics) |
| Strong field | RESTAT, World Development, Journal of International Economics |
| Specialty | Journal of Peace Research, Oxford Economic Papers |

---

## Common Data Sources

<!-- The Explorer prioritizes these. The explorer-critic knows their quirks. -->

| Dataset | Type | Access | Notes |
|---------|------|--------|-------|
| OECD CRS | project-level panel | public | Aid disbursements by donor, recipient, channel, sector — main outcome data |
| EM-DAT | event-level panel | public | Climate/natural disaster events, casualties, damages — main treatment source |
| GDIS | geospatial event panel | public | Subnational disaster boundaries — for spatial precision |
| World Bank WDI | country-year panel | public | GDP, population, governance covariates |
| Polity IV / V-Dem | country-year panel | public | Political regime controls |

---

## Common Identification Strategies

<!-- The Strategist considers these first. The strategist-critic knows field-specific threats. -->

| Strategy | Typical Application | Key Assumption to Defend |
|----------|-------------------|------------------------|
| Generalized event study (staggered DiD) | Disaster shocks on aid composition | Parallel trends across exposed/unexposed recipients; no anticipation |
| TWFE with multi-hazard exposure | Continuous treatment (hazard index) | Conditional exogeneity of disaster timing relative to aid determinants |
| Callaway-Sant'Anna / Sun-Abraham | Robust staggered DiD | Heterogeneity-robust; avoids negative weights from naive TWFE |
| Heterogeneity by sector/channel | Mechanism tests | Subgroup comparability conditional on treatment timing |

---

## Field Conventions

<!-- The Coder and Writer follow these. The writer-critic checks for them. -->

- Aid flow outcomes → use log(1+y) transformation or PPML for zero-inflated data; report both
- Always show event-study plots with pre-trends (k = -4 to -1 at minimum) before main table
- Cluster standard errors at recipient-country level (unit of treatment assignment)
- Report state vs. non-state channels separately — this IS the main decomposition
- Include donor fixed effects AND donor-year fixed effects where feasible (absorbs donor budget cycles)
- Governance controls (WGI composite or Polity) are expected by referees
- Distinguish humanitarian vs. development aid — EM-DAT disasters affect both differently
- PPML preferred over OLS for level regressions; log-linear for log regressions

---

## Notation Conventions

<!-- The Writer and writer-critic enforce these. -->

| Symbol | Meaning | Anti-pattern |
|--------|---------|-------------|
| $Y_{ijt}$ | Aid flow from donor $i$ to recipient $j$ at time $t$ | Don't aggregate to recipient-year without discussing composition |
| $D_{jt}$ | Disaster exposure for recipient $j$ at time $t$ | Distinguish binary event indicator vs. continuous hazard index |
| $\tau_k$ | Event-study coefficient at horizon $k$ relative to disaster | Always show pre-trends ($k < 0$) |
| $\alpha_{ij}$ | Donor-recipient pair fixed effect | Include in all regressions |

---

## Seminal References

<!-- The Librarian ensures these are cited when relevant. The strategist-critic knows their methods. -->

| Paper | Why It Matters |
|-------|---------------|
| Becerra et al. (2014) | Disasters and bilateral aid responsiveness — foundational empirics |
| Drabo & Mbaye (2011) | Climate disasters and aid allocation |
| Frot & Santiso (2011) | Aid fragmentation and channel choice |
| Callaway & Sant'Anna (2021) | Staggered DiD — the correct estimator for this design |
| Sun & Abraham (2021) | Heterogeneity-robust event study |
| Borusyak et al. (2024) | Imputation estimator for staggered DiD |
| Roodman (2011) | PPML for gravity-type aid models |

---

## Field-Specific Referee Concerns

<!-- The domain-referee and methods-referee watch for these. -->

- "Is disaster exposure truly exogenous?" — defend timing variation as conditionally random given pair FE + covariates
- "Parallel trends?" — show event-study pre-trends; discuss why pre-trends assumption is plausible
- "Why not naive TWFE?" — must use heterogeneity-robust estimator (CS, SA, or imputation)
- "Selection of recipient countries" — address whether more exposed countries differ in aid relationships
- "Mechanism: why governance aid increases?" — political economy argument (recipient bargaining) is central
- "Confounding with humanitarian crises?" — distinguish climate-related from conflict-related aid shocks
- "Donor heterogeneity?" — bilateral vs. multilateral donors may respond differently

---

## Quality Tolerance Thresholds

<!-- Customize for your domain's standards. Used by quality.md. -->

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Point estimates | 1e-4 | Panel DiD with clustered SE |
| Standard errors | relative 1e-3 | Cluster-robust at recipient country level |
