---
name: mathmodeling
description: "Solve, implement, and audit mathematical-modeling competition projects from problem decomposition through reproducible code, validation, sensitivity analysis, and contest-paper delivery. Use for 数学建模、国赛、美赛、华为杯、研究生数模、数模代码或论文终审; do not use for ordinary math homework or generic academic prose without a modeling task."
---

# Math Modeling Competition

Own the contest workflow from raw problem materials to a reviewable solution. Use Chinese for Chinese contests or Chinese paper requests; official contest language and submission requirements override local defaults. Preserve the user's requested scope, including read-only audits.

## Classify the request

- **Analyze:** produce the problem map, data/attachment audit, model candidates, validation plan, and blockers before implementation.
- **Build:** create independently runnable question entrypoints, shared modules, centralized parameters, results, and paper-ready evidence.
- **Review:** trace formulas, units, code, outputs, figures, tables, and claims back to source evidence.
- **Submission audit:** classify findings as `BLOCKER`, `MAJOR`, or `MINOR`; never call a structurally complete project mathematically validated.

## Non-negotiable rules

1. Inspect the original problem statement, attachments, appendix code, output requirements, and numeric conditions before implementation or benchmarking. For CUMCM, look for current-year official files and provenance in the current project directory first, then in an optional local archive at `$env:CSM_WORKSPACE\official\CUMCM\<year>` (an optional fallback that need not exist elsewhere). A missing local archive means the archive is missing, not that official files are absent, and is not by itself a reason to fetch from the web during the contest. Source priority, mirrors, and the training-plan/prior-year-format exclusion are defined in [references/cumcm-official.md](references/cumcm-official.md). Keep source facts, modeling assumptions, and proposals visibly separate.
2. Organize multi-question work in question order. Use one independently runnable `problem_i.py` per actual question and place shared logic beneath it. Do not invent four questions when the statement has another count.
3. Start with a transparent baseline. Baseline, selected model and fallback are roles, not a demand for three different implementations. A baseline that meets the task can be the final model. Prefer the simplest validated route; add at most one primary enhancement at a time, tied to a reproducible defect and a fair comparison.
4. Centralize paths, seeds, units, risk parameters, solver limits, and other experiment-defining values. Record parameter sources and information timing.
5. For optimization, report feasibility, termination status, objective convention, runtime, and—when applicable—optimality gap or bound. For stochastic work, report seeds, repetitions/scenarios, and uncertainty.
6. Separate knowledge type (`FACT`, `INFERENCE`, `ASSUMPTION`, `PROPOSAL`, `UNKNOWN`) from implementation/execution/verification progress. Never invent data, runs, metrics, p values, intervals, citations, improvements or verification. File presence, a solver call or an executed fit does not prove independent validation, physical truth or causal identification.
7. Tie every important paper claim and key number to a reproducible result artifact. Update the abstract last.
8. Set the actual deadline, finite search/trial/solver budget, model freeze and delivery reserve. Stop model expansion when the baseline meets the declared quality and validation criteria with no supported high-value gap, gains are below a practical threshold or repeat-run variation, or full validation and writing no longer fit. A runnable baseline is not the end of quality review. Do not spend the delivery reserve on another model by default.

## Default contest-paper delivery

- For a Chinese contest or Chinese paper request, write the paper—including captions and code comments—in Chinese LaTeX by default. An official contest class/template outranks this default; otherwise use UTF-8, XeLaTeX, and `ctexart`.
- The default paper deliverables are the reviewable `.tex` source and, when a TeX toolchain is available, the compiled PDF. Even when a contest permits Word, do not create or recommend DOC/DOCX unless the user explicitly requests it or PDF is forbidden.
- Compilation is not acceptance. Scan the build log, render every page, inspect equations/tables/figures/Chinese glyphs/page breaks, and fix material layout defects before handoff. Scope discipline for narrow requests, deliverable layout, figure/table rules, and the full build-and-QA loop are defined in [references/latex-paper.md](references/latex-paper.md).

## Route to the needed guidance

- Before choosing a model or touching code, read [references/problem-intake.md](references/problem-intake.md).
- For baseline/main/backup selection and model-family routing, read [references/model-routing.md](references/model-routing.md).
- For a full contest build or a time-limited modeling task, read [references/competition-budget.md](references/competition-budget.md) and scale it to the actual deadline. A short explanation does not require a full scaffold.
- For CUMCM preparation, a substantive full-solution quality review, or an explicit 国一/冲奖 target, read [references/competition-excellence.md](references/competition-excellence.md). It adds task-specific quality review, mathematical depth and a bounded improvement pass; it does not predict awards, trigger frontier research by itself, or expand a narrow editing request.
- For preparation, innovation/current research, or a validated baseline gap, read [references/innovation-routing.md](references/innovation-routing.md); it owns the whole frontier route—pre-contest anchoring, offline anchor matching during model selection, targeted gap search, the `$mathmodeling-frontier` handoff, claim level and fallback. Matching a prepared anchor is an offline lookup, never a search trigger, and the specialist keeps the only anchor/evidence catalog; do not start a second one here.
- [archive/frontier-modeling-2026.md](archive/frontier-modeling-2026.md) is a compatibility archive and offline query seed only. Do not load it for a routine task and never use its date or model cards as proof of currentness. If the specialist is unavailable, use equivalent live primary-source search and preserve the same hand-off/evidence fields.
- For implementation checks, uncertainty, sensitivity, solver evidence, reproducibility, or final auditing, read [references/validation-audit.md](references/validation-audit.md).
- For recording run/claim evidence or using the audit CLI, read [references/project-evidence.md](references/project-evidence.md).
- For a contest paper, abstract, figures, evidence map, or defense material, read [references/writing-evidence.md](references/writing-evidence.md).
- For CUMCM official rules, current-year source priority, format/submission limits, or AI-use disclosure, read [references/cumcm-official.md](references/cumcm-official.md) and refresh its dated snapshot before relying on it for a later contest year.
- For Chinese LaTeX paper source, compilation, page-layout QA, or PDF delivery, also read [references/latex-paper.md](references/latex-paper.md).
- When a specialized Nature Skill could improve figures, statistics, citations, or language, read [references/nature-collaboration.md](references/nature-collaboration.md) and use only an installed, relevant skill.

Read only the needed references and selected anchors; reuse guidance already read unless it changed. The ordinary route is intake → offline anchor matching and classic baseline → validation → warranted improvement → evidence → writing. Ordinary citations, abstracts, nonlinearity, graphs, PDEs or control do not themselves trigger broad online research. Preparation can produce sourced family anchors without an actual contest problem; adoption still requires a credible task baseline and local validation.

## First useful output

Unless the user asks for a narrower deliverable, give a compact reviewable first draft containing:

1. the artifact inventory and unresolved source gaps;
2. a question map with inputs, outputs/decisions, coupling, evaluation criteria, and acceptance evidence;
3. a baseline, whether a distinct main/fallback is needed, and the reason each role fits; only if research was triggered, add the minimal candidates with claim level, specialist status, evidence IDs, implementation risk and the defect addressed; three risk tiers are optional, not three required implementations;
4. a validation and sensitivity plan established before seeing favorable results;
5. the implementation/deliverable plan and current blockers;
6. for a deadline-bound task, the model-freeze time, the stopping criterion that ends model expansion, and the fallback—stated now, before any result looks favorable. The criteria themselves are in [references/competition-budget.md](references/competition-budget.md).

Explain the mechanism and modeling judgment before algorithm names. Ask only for missing information that would materially change the solution; otherwise make reasonable, labeled choices and continue.

## Project helpers

Resolve helpers from the installed Skill, not the current project directory. Initialize only when a new project is needed. Replace the example count with the actual number; `--problems` is required:

```powershell
$modelingSkill = Join-Path $HOME ".codex\skills\mathmodeling"
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "项目标题" --dry-run
python -X utf8 "$modelingSkill\scripts\init_project.py" "<project-dir>" --problems 2 --title "项目标题"
```

Audit submission structure and traceability:

```powershell
$modelingSkill = Join-Path $HOME ".codex\skills\mathmodeling"
python -X utf8 "$modelingSkill\scripts\build_paper.py" "<project-dir>"
python -X utf8 "$modelingSkill\scripts\audit_project.py" "<project-dir>" --strict --format markdown --report docs/structural_audit.md
```

`STRUCTURE_CHECKS_PASSED` means only that the implemented structural checks passed with independent review still required; it never means mathematically validated or submission-approved. Initializer reruns, auditor limits, report ownership, and legacy-project handling are defined in [references/project-evidence.md](references/project-evidence.md).

## Severity gate

- `BLOCKER`: missing or contradictory source/attachment evidence; unresolved implementation placeholders; missing question entrypoint, result, or final paper; infeasibility or a critical numeric contradiction.
- `MAJOR`: weak baseline, missing validation/robustness, undocumented solver status/gap, uncontrolled randomness, or an unsupported important claim.
- `MINOR`: wording, formatting, naming, or non-critical presentation defects.

In strict submission mode, no `BLOCKER` or `MAJOR` may remain. State the exact verification boundary in every final handoff.
