# Contest paper and evidence delivery

The paper is the final interface to the judges, but it must stay downstream of reproducible results.

Never fabricate experimental runs, data, scores, improvement percentages, p values, intervals, citations or verification. Do not write an unexecuted proposal as completed, an inference as a source fact, a simulation as an observation, or theoretical plausibility as empirical confirmation. Keep knowledge type and execution/review state separate; missing evidence remains explicit until resolved.

## Chinese contest-paper spine

Adapt the exact headings to the contest template:

1. 摘要与关键词
2. 问题重述
3. 问题分析（逐问给出机制、难点和路线）
4. 模型假设与符号说明
5. 数据来源、预处理与质量审计
6. 各问模型建立、求解与结果
7. 模型检验、敏感性、稳健性与不确定性
8. 模型评价、局限与改进
9. 结论、建议或应用解释
10. 参考文献、附录、代码/AI 使用披露（按规则）

Keep each question recognizable. Shared methods may be factored out, but do not make the reader reconstruct which model answers which question.

## Abstract contract

Write the abstract last. Include:

- one short sentence on the overall task and decision context;
- for each question: method, why it fits, one or two decisive quantitative results under explicit conditions, and the conclusion;
- the strongest validation/robustness evidence;
- a final practical implication or model-strength sentence with no unsupported superlatives.

Every number in the abstract must be traceable to a canonical result artifact and consistent with the body/table/figure. Avoid saying “显著提高、精准、最优、有效” without a baseline, metric, uncertainty, or solver evidence.

For a complete contest solution, make every requested answer findable in the corresponding question section: quantity/decision, units, conditions, uncertainty or feasibility boundary, and required result-file location. Explain why the result changes or remains stable across important conditions; a long list of algorithm names is not a contribution. Keep model construction, solution method and validation roles distinct. In a quality review, use competition-excellence for substantive reasoning and guosai-paper for Chinese expression; do not embellish unsupported results.

## Innovation claims and verbs

Match the verb to what was actually done:

| Verb | Evidence boundary |
|---|---|
| `applied / 采用 / 应用` | Used an existing method without a substantive structural change. |
| `adapted / 适配` | Changed inputs, constraints, loss, features, or workflow for this problem; document the change. |
| `integrated / 集成` | Connected existing modules with explicit roles and data flow; claims of module benefit/interaction require matching comparisons or ablation. Ordinary pipeline description is not such a claim. |
| `improved / 改进` | Requires a named baseline, identical protocol, metric and uncertainty showing the improvement. |
| `introduced / 引入` | Brought an existing component into this solution; does not mean the method was invented. |
| `proposed / 提出` | Reserve for a clearly specified construction attributable to this work; method-level novelty needs derivation and stronger comparison. |

These verbs are the writing-side view of the same grading as `claim_level` Level 0-4 in [innovation-routing.md](innovation-routing.md#论文主张分级); keep the two consistent and do not let a verb outrank the level the evidence supports. These verb rules suffice for ordinary writing. Read [innovation-routing.md](innovation-routing.md) only when the paper actually claims an innovation or needs its research handoff; do not load it for a normal abstract or bibliography. Existing-model use or tuning cannot be inflated into structural innovation.

Unless supported by a documented literature search and task-specific evidence, do not write “首次提出”, “国际领先”, “填补空白”, or equivalent priority claims. Do not write “显著优于” without a defined statistical or practical criterion, “证明了因果关系” without identification evidence, or “具有强泛化能力” without appropriate distribution/region/regime holdout tests. When causal effects are only partially identified, report “在所列假设下得到效应界/可行区间” and its width/sensitivity; never present the midpoint as an identified effect. Prefer bounded wording such as “在本题数据、所述划分与指标下”“结果表明/支持”“集成”“适配”“观察到”.

For every claimed innovation, the evidence map should add: baseline weakness, module role, implementation status, ablation artifact, gain/cost, failure regime, literature/source status, and the exact paper sentence. Candidate or `WATCH` methods belong in discussion/future work, not in the abstract as completed contributions.

## Claim-to-evidence map

Maintain a table like:

| Claim ID | Question | Run ID | Paper claim | Source artifact | Metric/value | Conditions | Paper location | Verification |
|---|---|---|---|---|---|---|---|---|
| C-01 | 1 | q1-run-id | ... | `results/tables/...csv` | ... | seed/scenario/split | 摘要/§5.2 | unverified |

Use it to reconcile narrative, tables, figures, and appendix. A missing source artifact is not repaired by softer wording alone.
Use exact `verified`/`unverified` or `已核验`/`未核验` states; a word embedded in `unverified` is not verification. The audit-ready column/run contract is in [project-evidence.md](project-evidence.md); source facts and assumptions can stay in the intake records rather than duplicating every sentence in this result-claim table.

## Figures and tables

- Each figure answers one modeling question. State data source, unit, uncertainty/interval, sample/scenario count, and relevant condition.
- Use consistent names, colors, scales, precision, and baseline labels across paper and presentation.
- Prefer readable direct labels and meaningful comparisons over decorative complexity.
- Keep generated tables machine-readable and render publication versions from them.
- Inspect crops, legends, Chinese fonts, overflow, and caption claims visually; file creation is not visual QA.

## Paper-ready project evidence

Retain:

- original source/attachment inventory and fixed definitions;
- centralized parameters and environment/solver information;
- one independently runnable entrypoint per question;
- canonical processed data, results, figures, tables, and concise run logs;
- model/assumption contract, validation report, evidence map, and AI usage log;
- final LaTeX source and compiled PDF; retain presentation files only when a presentation was explicitly requested.

When the current rules require AI disclosure, retain the internal AI usage log and generate the required disclosure PDF from a LaTeX source. For the 2026 CUMCM snapshot, the paper places an “AI 工具使用声明” before the references, and an AI-using team includes `AI工具使用详情.pdf` in the supporting materials with tool/version, purpose and stage, representative prompting process, adoption/manual revision, and verification. Re-check the current-year rule before submission rather than copying this snapshot forward unchanged.

Record who actually verified the work. Assistant checks, independent program reruns and team-member human review are distinct evidence; do not write that teammates reviewed or understood a derivation without their actual confirmation. Finish authorized technical work and clearly identify any remaining team review without inventing it or repeatedly asking permission to proceed.

Clean disposable caches and inspection intermediates only after acceptance; preserve sources, code, final deliverables, and reproducibility evidence.

## Final reading pass

Read in this order:

1. abstract against canonical results;
2. problem analysis against the original statement;
3. equations against symbol table, units, and code;
4. results against tables/figures and validation;
5. conclusions against evidence strength;
6. unexecuted work against the final PDF: read every `PROPOSAL` and `UNKNOWN` entry in `docs/assumptions.md`, search the final PDF text for each one, and confirm it appears only in limitations/future work, never as a completed contribution;
7. references, appendix, file naming, anonymity, AI disclosure, and current-year official rules.

Only when presentation delivery is requested, default to Chinese when appropriate and render every slide for overflow/crop checks. Use the presentation-specific skill for the actual PPTX workflow when available.
