# Problem intake and evidence contract

Use this reference before model selection, implementation, benchmarking, or comparison with an excellent paper.

## 1. Inventory the actual evidence

Read or list, as applicable:

- the original problem PDF/DOCX and every attachment;
- the current-year official contest rules, paper-format specification, submission notice, AI-use rule, and any regional additions, with source URL, publication date, local path, and superseded-version note;
- appendix code, field descriptions, units, legal option sets, and numeric conditions;
- required outputs, page/file limits, judging criteria, and disclosure rules;
- any baseline/excellent paper in its original form, including its appendix code and numeric results;
- the current README, configuration, entrypoints, outputs, and run logs.

Do not treat a file-list audit as a content audit. Do not infer row counts, time granularity, feasibility, scale, or solver availability from a summary or prior conversation.

For CUMCM work, check the current project directory first, then an optional local archive at `$env:CSM_WORKSPACE\official\CUMCM\<year>`. A missing local archive means the archive is missing, not that official files are absent. If the current national file is missing or older than the contest year, verify `mcm.edu.cn` live and archive the source or an explicitly labelled official-partner mirror. Do not promote a university training plan, local selection notice, or prior-year `format*.doc` to national-rule status.

## 2. Separate knowledge type from review progress

Maintain these labels in notes and deliverables:

- **FACT:** directly sourced observation or literal executed output; record its source and conditions. Execution alone does not verify the resulting interpretation.
- **INFERENCE:** deduction or estimate from explicit premises; record reasoning, assumptions and scope. Prediction is not causal identification.
- **ASSUMPTION:** introduced to make the model identifiable or solvable; give its consequence and a test where possible.
- **PROPOSAL:** a candidate method or experiment not yet implemented.
- **UNKNOWN:** missing or unidentifiable information; state its effect on the solution and how to resolve it or bound the claim.

Separately record progress as `not_implemented`, `implemented`, `executed`, or `verified` where applicable. Source-only claims can be `unverified`/`verified` without an implementation stage. Do not replace knowledge type with VERIFIED, label an executed model PROPOSAL, or treat an unknown deployment condition as an established fact.

Freeze contested definitions—time/season, population, capacity, cost, profit, information timing, correlation, and evaluation denominator—before comparing numbers.

## 3. Build the question map

Create one row per actual question:

| Field | Required content |
|---|---|
| Requested output | decision, forecast, ranking, explanation, policy, or simulation result |
| Exact deliverables | every requested sub-output, specified table/file/coordinate/strategy, scenario and precision; a method description alone is not the answer |
| Inputs | source file/field, unit, granularity, and availability time |
| Decision/unknowns | variables or quantities to infer |
| Mechanism | causal/domain logic that must be represented |
| Coupling | dependencies on other questions and shared parameters |
| Metric | judge-facing metric and internal diagnostic metrics |
| Acceptance evidence | file, table, figure, test, or calculation that will prove completion |
| Main risk | data, identifiability, computation, or claim-boundary risk |

For multiple questions, decide explicitly what is shared and what must remain independent. An independently runnable `problem_i.py` should answer exactly one question.

Trace cross-question inputs and assumptions. If an upstream fit, definition or exported parameter changes, identify downstream runs, decisions and paper claims needing refresh. Do not mix a new first-question model with stale later-question outputs. For a high-quality full solution, use the task-specific review in [competition-excellence.md](competition-excellence.md), rather than inventing generic judging weights.

## 4. Audit data before modeling

Record:

- schema, units, types, key uniqueness, joins, and missingness;
- valid ranges/options, impossible combinations, duplicated or inconsistent records;
- time and spatial granularity, sample size, censoring, and selection effects;
- outliers and whether they are errors, rare events, or decision-relevant extremes;
- training/validation information boundaries and leakage risks;
- transformations, imputation rules, aggregation loss, and parameter provenance.

Also make the following decisions explicit:

| Check | Required distinction |
|---|---|
| Independent units and complexity | Count entities, groups, time points, cycles and minority events separately. Rows/repeated measurements are not automatically independent samples. Use stable holdout performance to control complexity, not a universal sample/parameter ratio. |
| Deployment target | Future values for known entities, new entities, new regions, interpolation, or intervention? Choose time/group/spatial validation accordingly. |
| Availability per feature | Planned/known future covariates versus realized future observations or later revisions. Unknown future inputs need a past-data forecast or a labeled scenario, not their eventual true values. |
| Learned preprocessing | Fit imputation, scaling, decomposition, feature selection, graph construction and tuning inside the relevant split. Audit overlapping windows and simulation/observation reuse. |
| Causal roles | If actions are said to change outcomes: specify treatment, outcome, confounders/mediators, timing, estimand, overlap and interference. If identification is unsupported, retain association/scenarios or justified effect bounds. |
| Metric versus actual objective | Freeze horizon, denominator, units, misclassification/decision costs and optimization direction. Better prediction error alone does not establish better decisions. |

If attachments are absent or their fields cannot support the requested output, report the identifiability gap before proposing sophisticated methods.

## 5. Freeze a model contract per question

Before coding, write:

- sets/indices, parameters with units and sources, decision/state variables;
- objective or target, direction of optimization, constraints, and boundary/initial conditions;
- what is observed when each decision is made;
- baseline, main model, backup, validation protocol, and stopping rule;
- expected outputs and their canonical artifact paths.

These model roles may use the same implementation. For a full contest, set the resource budget and freezes using [competition-budget.md](competition-budget.md). Reuse an existing contract rather than creating another document for a narrow task. If critical sources, data or resource limits remain unresolved, mark the contract `PROVISIONAL`; return bounded analysis and a resolution plan rather than a final verified recommendation.

Use dimensional analysis and at least one hand-checkable toy case. This contract is the reference when code, paper, or results disagree.

## Initial deliverable template

Return: evidence inventory → source gaps → question map → frozen definitions → baseline/main/backup → pre-registered validation → implementation order → blockers. Keep facts, assumptions, and proposals in separate subsections.
