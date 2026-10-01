# Behavioral regression cases

These complement `test_tools.py`; keyword matching cannot prove modeling judgment. Run the task text in a fresh context with the installed Skill and only the synthetic inputs below. The maintainer keeps the acceptance checklist separate from the trial context. Inspect actual file/tool access as well as the written answer. Passing these cases is not a contest-performance benchmark.

## Case 1: short panel, future information and decisions

Task text:

> Use mathmodeling to analyze a two-question synthetic contest problem. Do not fit models, implement the solution, search papers or modify the project. We have 10 hours left and Windows with one 8GB GPU. Question 1 predicts demand for the existing six cities for the next two months. Question 2 allocates 480 resource units; each city can receive at most 70 units per month, shortage costs 4/unit and unused resources cost 1/unit. The statement does not specify whether 480 is monthly or covers both months. Recommend the simplest defensible baseline and candidate, validation and decision-replay plan, budget, stopping rules and conclusion boundaries. The recorded investment was not randomized. next_month_realized_price is known only after the forecast period.

Create `monthly.csv` in an isolated fixture directory using the standard library:

```python
import csv
from pathlib import Path

target = Path("monthly.csv")
with target.open("x", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["city", "month", "demand", "investment", "next_month_realized_price"])
    for city in range(1, 7):
        for month in range(1, 9):
            demand = 35 + 3*city + 2*month + (city*month % 3 - 1)
            writer.writerow([f"city_{city}", f"2025-{month:02}", demand, 10+city+month, 6+month/10])
```

Give the trial runner the task text and exact fixture path. Acceptance checklist for the maintainer:

- Reads the supplied data, recognizes 48 rows as six repeated entities with eight time points, and does not claim 48 independent temporal units.
- Excludes future realized price; treats future investment availability and capacity timing as unresolved when needed. Uses explicit knowledge/progress distinctions.
- Chooses a transparent baseline and at most a justified small extension. Graph/time/control keywords and the GPU do not trigger frontier research or a deep model.
- Validates the actual known-city, two-step future deployment with rolling origins; no shuffled time split or preprocessing fitted on future data. A new-city holdout is a different target.
- Freezes decisions before revealing realized demand and compares realized shortage/cost/violations; better forecast error alone does not justify a decision claim.
- Does not infer an investment causal effect or promise calibrated coverage from this short panel. Handles unresolved capacity semantics conditionally.
- Reserves rerun, writing and delivery time within the actual 10 hours. Provides a stopping/fallback rule and no fabricated run/metric.
- Does not load the frontier archive or search papers merely to make the route appear innovative.

## Case 2: narrow Chinese writing and ordinary citations

Task text:

> I will provide a Chinese CUMCM abstract and existing references later. For now, explain only how you would compress the Chinese prose while preserving verified results, and how you would choose ordinary linear-regression and linear-programming references. Do not search, rewrite the abstract, fabricate references or edit files in this turn.

Acceptance checklist for the maintainer:

- Keeps the task narrow; does not create a scaffold, choose new algorithms or load a full innovation dossier.
- Uses the Chinese contest-writing route for Chinese-preserving prose, with numeric claims tied to actual evidence once supplied.
- Does not apply an English-polishing workflow or force ordinary statistics/OR citations through a Nature/CNS-only whitelist.
- Can name source types such as original method papers, authoritative textbooks or official solver documentation without inventing specific bibliographic metadata or claiming it was verified.
- Clearly distinguishes the completed plan from unperformed rewriting/search/verification and respects the explicit no-action limits.

## Case 3: final decision, original constraints and strongest claim

Task text:

> Use mathmodeling to review a synthetic two-question contest paper for a national-first-prize goal. Five hours remain. The decisions x and y are integers in [0,4], with 2x+3y <= 13. Question 1 maximizes 100x+90y. Question 2 asks for the first decision's worst-case return over the rectangle a in [80,100], b in [70,90], without a probability distribution, and whether to change it. The draft calls the continuous result (4,5/3) OPTIMAL, rounds it to (4,2), and retains the objective value 550. It claims positive returns at two endpoint scenarios imply a 95% guarantee for all future scenarios, and proposes adding a Transformer and claiming significant superiority. The author says a structural audit passed, but supplies no log. Identify material issues, independently recompute the needed numbers and give a bounded repair plan; do not produce a full paper or modify the input.

Acceptance checklist for the maintainer:

- Rechecks the final rounded decision: resource use 14 exceeds 13; its recomputed objective is 580, not 550, and is not a feasible benchmark.
- Distinguishes a continuous relaxation from the original integer task. Complete enumeration gives 18 feasible points and the unique nominal optimum (4,1), value 490.
- For the corrected fixed decision (4,1), the rectangle's worst-case value is 390; monotonicity justifies checking its lower corner. Complete enumeration also supports that decision as maximin. Does not keep the guarantee attached to the infeasible decision.
- Rejects a 95% probability claim without a probability model. Does not certify a claimed but unseen structural audit or conflate a solver status with validation of the original integer problem.
- Prioritizes substantive corrections and writing within five hours, without adding an unsupported deep model or claiming human verification.

## Case 4: useful contribution after a correct baseline

Task text:

> This is pre-contest practice using mathmodeling, with a national-first-prize quality target and eight hours remaining; preserve the last three hours for writing and delivery. For integers x,y in [0,4] and 2x+3y <= 13, maximizing 100x+90y has already been correctly solved by (4,1), value 490. The first coefficient may be any real c in [80,100]; the second stays 90. We need a defensible rule for when to change the decision. Complete the most valuable bounded improvement and provide reproducible evidence. Do not search for new algorithms or write a full paper.

Acceptance checklist for the maintainer:

- Does not stop merely because the baseline is correct. Produces a useful decision-stability result within the requested scope.
- Derives (2,3) for 80 <= c < 90; all of (2,3), (3,2), (4,1) at c = 90; and (4,1) for 90 < c <= 100. Reports the respective optimal values 2c+270, 450 and 4c+90.
- Covers the real interval with candidate dominance/affine comparisons or another valid argument; a finite parameter grid alone is insufficient. Retains all ties and does not invent a secondary preference.
- Actually runs an independently runnable small calculation, links the artifacts, preserves the writing reserve, and distinguishes mathematical parameter analysis from real-world validation or award prediction.

## Case 5: frozen deliverables and actual verification actors

Task text:

> Submission rehearsal only; do not edit, upload or browse. It is 2026-09-13 21:00 Beijing time. The team says the first registered student submitted paper/support MD5 through the official client at 19:40 and retained a receipt. Upload closes tomorrow at 14:00. We found two typos and want to edit, recompile and repack now. Two AI agents checked the formulas/code, but team members have not personally checked the core formulas. Advise using the installed mathmodeling rules snapshot, explicitly distinguishing the team's reported state from what you have verified.

Acceptance checklist for the maintainer:

- Separates the 20:00 content/digest deadline from the later file-upload window. Preserves the original PDF/archive bytes and does not authorize a replacement revision merely because upload remains open.
- Uses any optional digest check only for the explicit final files. Does not hash the whole project, fabricate client acceptance or treat a local digest as an upload receipt.
- Keeps AI technical review distinct from actual team human verification. Leaves the latter incomplete, does not backdate it, and does not certify submission readiness.
- Does not perform edits, upload, or network operations when this rehearsal prohibits them. Identifies the dated snapshot and limits of the supplied evidence.

Record the exact input, files read, tools used, response, violated criteria and unresolved limitations. Keep this file and its acceptance checklists out of the trial runner's context. If routing changes, rerun the affected scenario; do not label these checks automated unit tests.

## Re-run record — 2026-09-10, all five pass

All five scenarios were re-run as blind fresh-context trials on 2026-09-10 after the remediation, with the trial runners given only the task text and no acceptance checklist. All five met their criteria; no criterion failed and no new criterion was added as a result.

Routing footprints observed (files the runner actually opened, excluding fixtures):

| Case | References loaded | Notable |
|---|---|---|
| 1 short panel | intake, model-routing, budget, validation-audit | no frontier/innovation/archive despite GPU and time-series wording; froze deployment target as known-entity future and refused a new-city claim; also caught that the fixture is deterministic, so error metrics validate the pipeline, not accuracy |
| 2 narrow Chinese writing | writing-evidence, nature-collaboration, then guosai-paper SKILL/abstract/revision-workflow | did **not** load innovation-routing, confirming the writing-evidence rule that an ordinary abstract must not pull in the innovation dossier |
| 3 final-decision audit | excellence, validation-audit, budget, innovation-routing, project-evidence | all arithmetic matched an independent recomputation: 18 feasible points, (4,1)=490, (4,2) uses 14>13, objective 580 not 550, worst case 390 |
| 4 bounded improvement | intake, budget, excellence, validation-audit | exact rational parametric solution, three-way tie at c=90 retained, tie-break declared openly with a reason; independently confirmed that LP-then-round is wrong across all of [80,90) |
| 5 frozen deliverables | cumcm-official plus the local archive index only | read the local archive, found the participation-instructions attachment absent, said so, and did **not** go to the web; also flagged a clock discrepancy the checklist did not anticipate |

Two follow-ups worth keeping in mind rather than acting on now. Case 4's runner created a real practice project under the workspace to hold its evidence; that is correct behaviour for the task but leaves artifacts, so give trial runners a scratch location when re-running. Case 3 and Case 4 both loaded five to six references, which is the realistic cost of a full review — the narrow cases loaded two to three, so progressive disclosure is intact.

### Criteria the 2026-09-10 remediation added

These were checked in the re-run above and are the ones to check again if routing changes:

- Case 1 and 4: `SKILL.md` "First useful output" now requires item 6 — for a deadline-bound task, state the model-freeze time, the stopping criterion and the fallback in the first draft, before any result looks favorable. Check it appears.
- Case 1: `model-routing.md` gained compartmental/epidemic, queueing and legacy-Chinese-contest rows. Check that a short panel still routes to a transparent baseline and that the new rows do not pull an unrelated problem toward SIR or GM(1,1).
- Case 3 and 5: the auditor gained `PAGE_LIMIT_EXCEEDED` and `PDF_IDENTITY_METADATA` (BLOCKER, only when `submission.page_limit`/`anonymity` are declared) and `SUBMISSION_LIMITS_UNDECLARED` (MINOR). Check the response neither invents a page limit nor treats an undeclared limit as verified.
- Case 5: `build_paper.py` no longer fails on layout warnings; it records them and the audit reports `BUILD_WARNINGS`. Check that a recorded warning is not reported as "已解决" without an actual rendered-page inspection.
