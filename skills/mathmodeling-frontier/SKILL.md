---
name: mathmodeling-frontier
description: "Prepare literature-backed algorithm anchors before mathematical-modeling contests, match them to each problem offline, and search targeted gaps during the contest. Use for 赛前算法储备、按题型锚定、数模创新、前沿算法、最新模型、模型选择、找新论文、赛时补漏; do not use for unrelated literature reviews or replace source/data auditing."
---

# Math Modeling Frontier

Prepare research before the contest so topic-specific work can start from checked methods. This skill owns the reusable algorithm/evidence anchors; `$mathmodeling` owns the actual problem, implementation, validation and paper. A prepared anchor is a starting hypothesis with alternatives, not a prescribed winning model.

## Classify the request

- **Pre-contest preparation:** search across requested problem families now and maintain dated anchors with mechanisms, baselines, deltas, rejection conditions, primary papers and resource status. No unseen contest statement is required for this reusable preparation.
- **Contest matching:** read the real statement/data, select only the relevant anchors offline, and map their conditions to this problem before implementation.
- **Gap refresh:** search only missing assumptions, new conditions, version/access changes or omitted alternatives around the selected anchors. This is the default contest-time research mode.
- **Focused research:** investigate a material gap absent from the library, within an explicit budget; expand beyond matching only when the evidence warrants it.
- **Model selection:** compare baseline, main, frontier, and backup models under the actual data and compute budget.
- **Innovation design:** define a minimal, testable delta over a transparent baseline.
- **Novelty audit:** detect stale citations, decorative complexity, fake novelty, weak benchmarks, or unsupported “state-of-the-art” claims.

## Non-negotiable rules

1. Do the broad primary-source search in pre-contest preparation. Reuse its verified evidence and original dates during offline matching; do not force a fresh search for every anchor or every question. An explicit claim about what is latest now still requires a bounded live refresh. Record exact queries, cutoff, version distinctions and failures; never relabel an old check as performed today.
2. Separate `PREPARED` family knowledge from a `FROZEN` problem contract. Without a contest statement, prepare sourced anchors and, within the requested scope, dependencies, pinned weights and representative local smoke tests now. Do not defer generic resource readiness until the contest; mark unperformed checks accurately. Before adopting or ranking for the real task, inspect its statement, attachments, information timing, data regime and limits. An incomplete task contract remains `PROVISIONAL`, but does not prevent useful preparation.
3. Search recent work and strong anchors together. Prefer official journal/proceedings pages and author preprints; label peer-review status and verify title, authors, year, DOI/identifier, code, data, and license when they matter.
4. Keep a transparent baseline, a justified main model, at most one primary innovation package, and a viable backup. Novelty alone is not evidence.
5. A frontier candidate must pass mechanism fit, data fit, compute fit, reproducibility, explainability, feasibility preservation, and a predeclared validation/ablation test.
6. Do not claim an algorithm is superior because its source reports good benchmark results. Re-run it, or a faithful reduced implementation, on the problem's own split/scenarios and compare under the same information, metric, seed, budget, and constraints.
7. Preserve mathematical guarantees. Learned predictions, branching, neighborhoods, policies, or generated scenarios may assist an exact/statistical model, but exported decisions must still pass independent feasibility, unit, objective, and boundary checks.
8. Keep publication status, implementation availability, local smoke testing and task validation separate. Unreviewed submissions, workshops and vendor releases remain exploratory evidence; local benchmark success does not turn them into peer-reviewed papers. Never hide unavailable code, data, weights, licenses or excessive hardware needs.
9. Tie the paper's innovation claim to a source, implementation, benchmark table, ablation, and failure boundary. Avoid “首次、显著、最优、先进” without a defined comparison and evidence.

## Respect the user's modeling-paper defaults

- Deliver Chinese-first analysis, code comments, figure labels, tables, and contest-paper prose unless another language is requested.
- Write paper material as compilable LaTeX by default. Keep equations editable, use consistent symbols and `\label`/`\ref`, maintain a real `.bib` or auditable bibliography, and never invent references.
- Keep the requested question order. When implementation is in scope, prefer independently runnable `problem_i.py`, centralized parameters, deterministic seeds, and paper-ready result exports.
- Produce a complete reviewable first draft before polishing isolated sentences. Separate literature claims, local experimental results, and unverified hypotheses.
- Preserve the professional gates of `$mathmodeling`; these preferences change presentation and workflow, not mathematical rigor.

## Route to focused guidance

- Start preparation, offline matching and contest gap checks with [references/precontest-anchors.md](references/precontest-anchors.md). Use the local lookup helper to read only selected routes and their linked evidence; do not dump the whole catalog into context.
- For an actual online search or schema-v2 ranking, read [references/live-search-protocol.md](references/live-search-protocol.md).
- To map problem signals to model families and reject conditions, read [references/problem-model-map.md](references/problem-model-map.md).
- To score candidates, design ablations, and write the innovation claim, read [references/innovation-gates.md](references/innovation-gates.md).
- [references/frontier-live-delta-2026-09-01.md](references/frontier-live-delta-2026-09-01.md) and [references/frontier-snapshot-2026-08-26.md](references/frontier-snapshot-2026-08-26.md) preserve earlier evidence and query seeds. The anchor catalog is the maintained lookup entry. Do not reload or refresh both archives merely because a task mentions innovation.

Read only the references needed for the current request.

## Working sequence

1. Identify the mode. In preparation, define family/data/resource envelopes and build checked anchors now. In contest matching, inspect the actual materials and select the applicable route(s), not a fixed topic letter.
2. Read the selected anchor's baseline, upgrade mechanism, applicability, rejection conditions, papers, resource unknowns and scoped gap queries. Map each to the actual question and retain a plausible competing explanation to avoid anchoring bias.
3. Freeze baseline, at most one primary enhancement, fallback, validation and budget. An anchor alone is not evidence of a local baseline defect or task performance.
4. If a material uncertainty remains, perform a targeted gap refresh. Stop when the decision-relevant uncertainty is resolved or the cap is reached; do not rebuild a six-model survey or re-read unrelated families.
5. Reuse source IDs/dates. For substantial task ranking, use schema v2 and `scripts/rank_candidates.py`; keep the preparation catalog separate from this task-specific matrix. Hard gates override score.
6. Implement the smallest faithful experiment, compare under the same information and budget, and test the added component when claiming its benefit. Promote only if task evidence supports a defensible improvement or new capability.

## Deliverable contract

For preparation, update the reusable anchors and their dated source log; keep downloaded originals and maintenance reports outside the Skill. For a substantial task-specific research run, retain only applicable deliverables:

- `docs/frontier_search_log.md`: date, queries, sources, failures, and deduplicated papers;
- `docs/innovation_matrix.json`: schema-v2 search metadata, frozen/provisional contract status, baseline IDs, deduplicated evidence IDs, candidate deltas, risks, code/data/resource status, fair protocols, ablations, and reject conditions; do not hand-write candidate status—`rank_candidates.py` derives it in the ranking output;
- `docs/innovation_dossier.md`: baseline, selected delta, model equations/architecture, applicability, reject conditions, and citations;
- `results/frontier_benchmark.*`: same-split comparison, runtime/compute, seeds, uncertainty, and ablation;
- `paper/sections/frontier_innovation.tex` and corresponding `.bib` entries when a paper is in scope;
- the paper-ready innovation paragraph and claim-to-evidence entries.

The first useful contest response is a selected anchor, its actual task fit, transparent baseline, warranted delta or reason to retain baseline, smallest fair check, and a short gap list. No gap means no mandatory literature run. Preparation without a contest statement delivers sourced conditional anchors now, not just a promise to search later. Keep unseen task outcomes and unavailable local resource checks unknown.

## Offline anchor lookup

```powershell
$frontierSkill = Join-Path $HOME ".codex\skills\mathmodeling-frontier"
python -X utf8 "$frontierSkill\scripts\lookup_anchors.py" --list
python -X utf8 "$frontierSkill\scripts\lookup_anchors.py" --task forecast --format markdown
```

The helper reads the bundled catalog only, makes no network call, writes no files and assigns no candidate score. Match the task conditions before trying a model. Its `PREPARED` label means literature preparation, not local readiness or superiority.

## Candidate ranking helper

```powershell
python scripts/rank_candidates.py docs/innovation_matrix.json --format markdown --output docs/innovation_ranking.md
```

The ranking helper validates schema links and entered evidence fields. Historical live checks can be reused with their actual dates; the compatibility field `live_search_verified` does not assert a network call occurred in the current task. It derives source counts from `evidence_ids`, forces unresolved feasibility/resources or a provisional contract to `WATCH`, and rejects hard-gate failures. It cannot determine mathematical correctness, literature completeness, actual human review or novelty.

## Severity gate

- `BLOCKER`: unsupported current-freshness claim; adopting a task model without inspecting original materials; no verified primary evidence; missing task baseline; fabricated citation/result; infeasible decision; leakage or invalid evaluation split. The absence of a future contest statement is not a blocker for pre-contest preparation.
- `MAJOR`: innovation is only a model name; no same-budget benchmark or ablation; preprint status hidden; code/data unavailable without disclosure; compute exceeds the contest budget; important negative evidence ignored.
- `MINOR`: incomplete metadata, weak wording, inconsistent naming, or non-critical presentation defects.

State the exact search cutoff and verification boundary in every final handoff.
