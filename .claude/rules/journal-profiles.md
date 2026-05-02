# Journal Profiles

<!--
These profiles calibrate the domain-referee and methods-referee when reviewing
for a specific journal. Each profile describes the journal's review culture
in plain language — the LLM adapts its priorities accordingly.

Used by: domain-referee.md, methods-referee.md (via /review --peer [journal])
-->

## How This Works

When `/review --peer [journal]` is invoked:

1. **Profile found below** → referees calibrate using the full profile
2. **Profile NOT found** → referees use the journal name + domain-profile.md to adapt (still better than generic)
3. **No journal specified** → generic top-field referee behavior

---

## Top-5 General Interest

### American Economic Review (AER)
**Focus:** All fields of economics — the broadest audience
**Bar:** Must interest economists outside your subfield. Big question, clean execution, clear contribution.
**Domain referee adjusts:** "Would a labor economist care about this health paper?" Contribution must be broad. Literature positioning against the *general* frontier, not just subfield. Policy implications welcome but not required — insight is enough.
**Methods referee adjusts:** Identification must be convincing to non-specialists. Clean, transparent design preferred over technically complex one. Standard errors and robustness should be thorough but not excessive.
**Typical concerns:** "Why should economists outside this field care?" "Is the contribution big enough for AER?" "Is this too narrow/specialized?"

### Econometrica (ECMA)
**Focus:** Theoretical and empirical economics with formal rigor
**Bar:** Methodological innovation or empirical work with exceptional identification and formal results.
**Domain referee adjusts:** Theoretical contribution valued highly. If empirical, the design must be near-airtight. Formal welfare analysis expected. Less emphasis on policy narrative, more on economic theory and mechanisms.
**Methods referee adjusts:** Formal proofs or near-formal arguments expected for key results. Asymptotic properties discussed. Novel estimators should have theoretical justification. Simulation evidence for finite-sample properties.
**Typical concerns:** "Where's the formal result?" "What are the asymptotic properties?" "Is this a methods contribution or an applied contribution?"

### Journal of Political Economy (JPE)
**Focus:** All fields — strong emphasis on economic mechanisms and structural thinking
**Bar:** Deep economic insight. JPE values understanding *why* something happens, not just *that* it happens.
**Domain referee adjusts:** Mechanism is king. Reduced-form results alone insufficient — need to explain the economics. Structural models or mechanism tests expected. Theoretical framework (even informal) valued.
**Methods referee adjusts:** Identification strong, but mechanism evidence equally important. Heterogeneity that illuminates the mechanism. Willing to accept some identification imperfection if the economic insight is deep enough.
**Typical concerns:** "What's the mechanism?" "Can you decompose the effect?" "What does this tell us about economic behavior?"

### Quarterly Journal of Economics (QJE)
**Focus:** All fields — prizes compelling narrative and important questions
**Bar:** The question must be important and the answer must surprise. QJE loves papers that change how you think about something.
**Domain referee adjusts:** Narrative matters enormously. The paper should read like a story with a punchline. Broad implications. Creative use of data or setting. "Clever" identification valued.
**Methods referee adjusts:** Identification must be clean and intuitive — not just technically correct, but easy to explain. Transparency and simplicity over complexity. Visual evidence (event studies, RD plots) highly valued.
**Typical concerns:** "Is this surprising?" "Does this change how we think about X?" "Can you explain the identification in one sentence?"

### Review of Economic Studies (REStud)
**Focus:** All fields — technically excellent empirical and theoretical work
**Bar:** Technical quality must be top-tier. Values precision and completeness over narrative.
**Domain referee adjusts:** Thoroughness expected — address every possible objection. Complete set of robustness checks. Careful literature review. Less emphasis on storytelling than QJE, more on completeness.
**Methods referee adjusts:** Every specification must be justified. Full battery of robustness checks expected. Sensitivity analysis (Oster bounds, etc.). Careful treatment of inference. Multiple testing corrections if applicable.
**Typical concerns:** "Have you checked robustness to X?" "What about specification Y?" "The inference needs more care."

---

## Top Field Journals

### American Economic Journal: Applied Economics (AEJ:Applied)
**Focus:** Empirical microeconomics — labor, health, education, development, public
**Bar:** Clean applied micro paper with credible identification and clear results. Slightly below top-5 bar but same rigor expectations.
**Domain referee adjusts:** Contribution should be meaningful to the subfield. Practical policy relevance appreciated. Literature positioning within the subfield, not the general field.
**Methods referee adjusts:** Same identification standards as top-5. Modern estimators expected (no naive TWFE for staggered). Replication package expected.
**Typical concerns:** "Is this incremental relative to [closely related paper]?" "Would this be better in a field journal?"

### American Economic Journal: Economic Policy (AEJ:Policy)
**Focus:** Policy evaluation and design — how policies affect outcomes
**Bar:** Must have direct policy relevance. Natural experiments from actual policy changes preferred.
**Domain referee adjusts:** Policy implications front and center — not an afterthought. Cost-benefit or welfare discussion expected. Institutional details of the policy must be well-documented. Generalizability to other policy contexts.
**Methods referee adjusts:** Identification from actual policy variation (not cross-sectional). Pre-trends must be clean. Heterogeneity by policy-relevant subgroups expected. Back-of-envelope welfare calculations.
**Typical concerns:** "What should policymakers do with this?" "Does this generalize to other states/countries?" "What's the cost-benefit?"

### Journal of Public Economics (JPubE)
**Focus:** Tax policy, public goods, redistribution, government programs
**Bar:** Public finance question with clean identification. Understanding of tax/transfer system mechanics.
**Domain referee adjusts:** Tax incidence, deadweight loss, behavioral responses to taxation. Program evaluation of government interventions. Fiscal federalism. Redistribution and inequality. Knowledge of tax code and transfer programs.
**Methods referee adjusts:** Bunching estimators for tax kinks/notches. RDD at eligibility thresholds. DiD around policy changes. Structural models of labor supply response. Extensive vs. intensive margin effects.
**Typical concerns:** "What's the elasticity?" "Extensive or intensive margin?" "Welfare implications of the tax/transfer change?"

### Journal of Development Economics (JDE)
**Focus:** Development economics — poverty, institutions, agriculture, trade in developing countries
**Bar:** Credible empirical evidence on development questions. RCTs or strong quasi-experimental designs. Field knowledge.
**Domain referee adjusts:** Context matters enormously — deep knowledge of the country/region expected. External validity to other developing country settings. Implementation details for interventions. Cost-effectiveness. Sustainability of effects. Gender and equity dimensions.
**Methods referee adjusts:** RCTs: randomization checks, attrition, compliance, spillovers, pre-analysis plan. Quasi-experimental: strong first stage for IV, clean RD, credible parallel trends. Power calculations. Clustered standard errors at appropriate level.
**Typical concerns:** "Does this generalize beyond this specific context?" "What about attrition?" "Cost-effectiveness?" "Long-run effects?"

### Journal of International Economics (JIE)
**Focus:** International trade, FDI, migration, exchange rates, international finance
**Bar:** Strong theoretical or empirical contribution to international economics. Gravity models, trade policy evaluation, and open-economy macro all welcome. Well-established top field journal.
**Domain referee adjusts:** Knowledge of trade theory (gravity, Melitz-type firm heterogeneity) and international finance expected. Policy implications for trade agreements, tariffs, capital flows. Aid flows with international trade or finance dimensions can fit here. Literature positioning against the international economics frontier specifically.
**Methods referee adjusts:** PPML standard for gravity-type regressions (same expectation as in development economics — see JDE). IV for trade policy endogeneity (shift-share Bartik instruments, tariff shocks). Cluster at country-pair or exporter level. Heterogeneity by country income, institution quality, or trade openness.
**Typical concerns:** "Is this consistent with trade theory?" "Have you addressed endogeneity of trade policy?" "Does PPML vs OLS change the result?" "What are the general equilibrium implications?"

### European Journal of Political Economy (EJPE)
**Focus:** Political economy of public policy — public choice, institutions, redistributive politics, political business cycles, aid and governance
**Bar:** Solid empirical or theoretical contribution to political economy. Lower bar than top-5 but rigorously peer-reviewed. European focus not required — global political economy questions welcome.
**Domain referee adjusts:** Mechanism connecting political incentives to economic outcomes is central — same instinct as JPE but applied to public choice and institutional questions. Rent-seeking, electoral cycles, donor motives, recipient bargaining power all in scope. Aid and disaster papers must frame the political economy channel explicitly.
**Methods referee adjusts:** DiD around elections, institutional changes, or disaster shocks standard. IV for political variables (same credibility bar as JPubE). Panel methods with country and time FE. Heterogeneity by institutional quality, regime type, or electoral cycle position.
**Typical concerns:** "What's the political economy mechanism?" "Is the political variable truly exogenous?" "How do institutions shape the disaster/aid relationship?" "Have you compared democratic vs. autocratic recipients?"

---

## Strong Field Journals

### Review of Economics and Statistics (RESTAT)
**Focus:** Empirical economics — all fields, emphasis on careful measurement and methods
**Bar:** Technically excellent empirical work. Values careful econometrics and measurement.
**Domain referee adjusts:** Measurement quality is paramount. Novel data or measurement approaches valued. Less emphasis on big-picture narrative than QJE, more on getting the econometrics exactly right. Replication studies welcome.
**Methods referee adjusts:** Highest econometric standards short of Econometrica. Every assumption must be tested or bounded. Sensitivity analysis expected. Careful treatment of standard errors. Pre-registration or pre-analysis plans viewed favorably.
**Typical concerns:** "Is the measurement precise enough?" "Have you tested every assumption?" "What about measurement error in [variable]?"

### AER: Insights
**Focus:** Same breadth as AER but shorter format — important results that can be communicated concisely
**Bar:** AER-quality insight in a shorter paper. Must be self-contained and punchy.
**Domain referee adjusts:** Brevity is a feature, not a limitation. One clean result is enough. No need for 15 robustness checks — the core result must be compelling on its own. Well-suited for striking findings or clever identification.
**Methods referee adjusts:** Core identification must be clean. Fewer robustness checks acceptable given format, but the main result must be robust. Transparency and visual evidence valued.
**Typical concerns:** "Can this be communicated in 10 pages?" "Is the single result compelling enough?" "Does this need a longer format to be convincing?"

### Economics of Disasters and Climate Change (EDCC)
**Focus:** Economic analysis of natural disasters, climate change impacts, adaptation, resilience, and disaster risk reduction
**Bar:** Credible empirical or modeling contribution on disaster/climate economics. Interdisciplinary work welcome. Specialty venue with a lower bar than top field journals — the question must fit the journal's narrow scope.
**Domain referee adjusts:** Deep knowledge of disaster data (EM-DAT, GDIS, geospatial exposure measures) and climate datasets expected — same data literacy as required by this project's design. Connection to disaster risk management literature and policy (Sendai Framework, IPCC). Humanitarian vs. development aid distinction valued. External validity to other disaster-prone settings (like JDE, context and generalizability matter).
**Methods referee adjusts:** Event study or DiD around disaster events is the standard design. Geospatial methods for physical exposure measurement welcome and expected. PPML for aid or damage flows. Robustness to disaster definition, severity threshold, and hazard type. Clustered standard errors at recipient-country level standard.
**Typical concerns:** "How do you define and measure disaster exposure?" "Is severity endogenous to aid or outcomes?" "Selection into affected areas?" "What does this imply for disaster risk reduction policy?" "How does this compare to existing EM-DAT-based estimates?"

### The Review of International Organizations (RIO)
**Focus:** International organizations, global governance, multilateral institutions — their design, effectiveness, and effects on policy
**Bar:** Credible empirical or theoretical work on IOs. Cross-disciplinary — accepts both economics and political science approaches. Contribution must speak to the IO literature specifically, not just use IOs as a context.
**Domain referee adjusts:** Knowledge of specific IOs (UN, IMF, World Bank, WTO, regional development banks) expected. Conditionality, delegation, IO effectiveness, and multilateral vs. bilateral comparisons are core questions. Aid channeled through IOs (vs. bilateral state channels) is directly relevant. Frame in terms of IO design and governance — not just development economics (same content, different frame from JDE).
**Methods referee adjusts:** Quasi-experimental designs around IO interventions or membership thresholds (RDD at eligibility, DiD around accession). IV for IO participation and conditionality endogeneity. Panel methods with country and time FE. Both reduced-form and structural models accepted — political science methods (matching, synthetic control) as credible as econometric designs.
**Typical concerns:** "Is IO participation endogenous?" "Which specific IO mechanism drives the result?" "Bilateral vs. multilateral comparison?" "What does this imply for IO design or reform?" "Have you distinguished IO type (humanitarian vs. development)?"

---

## Political Science Journals

*Note: These journals are in political science, not economics. Domain referees calibrate for a political science audience — causal identification standards are similar to economics, but framing, theory, and literature positioning must address political science debates (principal-agent theory, selectorate theory, IR liberalism/realism, comparative institutions).*

### American Political Science Review (APSR)
**Focus:** The flagship political science journal — all subfields (American politics, comparative, IR, formal theory, political methodology), highest prestige
**Bar:** Landmark contribution to political science. The result must be definitive, the question must matter to the discipline broadly. Must interest scholars across subfields, not just IR or comparative specialists. Same prestige ceiling as AER in economics.
**Domain referee adjusts:** Theoretical innovation or a definitive empirical result on a core political science question. Aid/disaster work must frame in terms of principal-agent theory, selectorate theory, conditionality debates, or donor-recipient bargaining — not just development economics. Normative political theory, formal models, and empirical work all considered. "Why should comparativists, IR scholars, and political theorists all care?" is the bar.
**Methods referee adjusts:** Empirical identification held to AER-level standards. Formal theoretical models expected for theory papers. Pre-analysis plans viewed favorably. Event studies, DiD, IV all accepted — but must be explained accessibly to a non-econometrics audience. Pre-trends plots and visual evidence valued (same as QJE instinct).
**Typical concerns:** "Is this contribution big enough for APSR?" "Does it advance political theory?" "Why should scholars outside your subfield care?" "Is the empirical design beyond reproach by political methodology standards?"

### American Journal of Political Science (AJPS)
**Focus:** All subfields of political science — American, comparative, international relations, political methodology — top field journal just below APSR in prestige
**Bar:** High. Must contribute to political science theory or empirics at the frontier. Strong causal identification required for empirical work. Slightly narrower contribution acceptable compared to APSR.
**Domain referee adjusts:** Same domain expectations as APSR but contribution can speak to a subfield rather than all of political science. Aid and disaster work must connect to political science questions: donor accountability, recipient regime type, humanitarian intervention motives. Economic framing alone insufficient — political science theory must anchor the contribution.
**Methods referee adjusts:** Same identification standards as APSR. Causal designs held to same bar as in top economics journals (DiD, RDD, IV). Formal models with testable implications valued alongside empirical tests. Pre-registration viewed favorably. Cluster at the appropriate political unit.
**Typical concerns:** "What does this contribute to political science theory?" "Is the causal identification credible by political methodology standards?" "Have you engaged the IR/comparative politics literature?" "How does this connect to regime type or institutional variation?"

### Journal of Politics (JoP)
**Focus:** All subfields of political science — similar scope to AJPS; published by University of Chicago Press for the Southern Political Science Association
**Bar:** Strong empirical or theoretical contribution to political science. Solid field journal, slightly below APSR/AJPS at the very top but still highly competitive. Generally accessible framing valued.
**Domain referee adjusts:** Similar domain expectations to AJPS. Electoral behavior, legislative politics, international relations, and comparative institutions all in scope. Aid/disaster papers welcome if the political economy framing is clear. Accessible to a broad political science audience — avoid excessive econometric jargon without explanation.
**Methods referee adjusts:** Credible identification required — DiD, IV, RDD all accepted. Simulation and formal theory welcome. Generally more tolerant of observational designs than AJPS if the argument is compelling and robustness is shown. Replication package expected at acceptance.
**Typical concerns:** "What's the political science contribution?" "How does identification compare to best practice in political methodology?" "Is this theory-driven or purely empirical?" "What are the implications for democratic governance or institutional design?"

---

## Add Your Own Journal

Copy this template and add it above this section:

```markdown
### [Journal Name] ([Abbreviation])
**Focus:** [fields and topics covered]
**Bar:** [what it takes to publish here]
**Domain referee adjusts:** [what matters most to domain reviewers at this journal]
**Methods referee adjusts:** [rigor expectations, preferred methods, required checks]
**Typical concerns:** [common referee questions at this journal]
```
