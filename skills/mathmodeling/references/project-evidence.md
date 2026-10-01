# Minimal project, run and claim contract

Read when recording executions or using the project auditor. This contract links evidence; it does not prove that a declaration is true or that a numerical/modeling claim is correct. Do not generate additional files per action.

## Project manifest and legacy projects

`mathmodeling.json` schema 2 keeps the existing question count, entrypoints and canonical directories, and adds `source_files`, `run_manifest` and `submission`. Initialize with the actual `--problems` count. Each entrypoint is a distinct project-relative Python file; list order maps to questions 1..N. `source_files` lists the statement and required attachments, including files under `data/raw` or `docs/sources`; their content/roles are checked in the source inventory.

All declared artifact paths are relative to the project; `..`, absolute paths and links escaping the project are rejected. Archive required external inputs or adapt the chosen project root rather than granting a manifest arbitrary filesystem access. Customize existing canonical paths and `submission.source`/`submission.pdf` instead of creating a second project layout. Initializer reruns preserve existing files and reject changed question counts/custom path layouts before writing.

The auditor reads valid schema 1 manifests without changing them. It reports missing run/claim/build contracts; it never automatically upgrades old reports or invents missing execution. Without a manifest, `--problem-count` supplies the actual scope; discovered entrypoints alone cannot prove all questions are covered. A conflicting explicit count is an error.

## One selected run per question

Keep exploratory successes/failures in concise ordinary logs. `results/run_manifest.json` (or the manifest's `run_manifest` path) contains only the currently selected run for each question. Write it from the real execution after saving outputs and validation. The following is a schema example, **not evidence that an experiment was executed**; replace values from actual records.

```json
{
  "schema_version": 1,
  "runs": [{
    "question": 1,
    "run_id": "q1-selected-run",
    "model_kind": "regression",
    "status": "completed",
    "command": "python -X utf8 problem_1.py",
    "environment": "actual Python, dependency and solver versions",
    "started_at": "2026-09-05T10:00:00+08:00",
    "finished_at": "2026-09-05T10:01:00+08:00",
    "runtime_seconds": 60.0,
    "inputs": ["data/raw/problem.txt", "data/raw/observations.csv"],
    "code": ["problem_1.py", "src/common/model.py", "config/parameters.yaml"],
    "artifacts": ["results/tables/q1.csv"],
    "validation": {
      "status": "passed",
      "protocol": "actual split, deployment target and independent check",
      "baseline_artifact": "results/tables/q1.csv",
      "artifacts": ["results/tables/q1_validation.csv"]
    },
    "randomness": {"mode": "deterministic"},
    "file_stamps": {}
  }]
}
```

`model_kind`: regression, classification, prediction, time_series, panel, graph, optimization, prediction_optimization, multi_objective, robust_optimization, causal, uncertainty_quantification, simulation, inverse, analytical, ranking or clustering. A deterministic analytical solution need not invent random seeds; it still records the calculation/check actually run and the resulting proof/calculation artifact. Stochastic work uses `{"mode":"stochastic","seeds":[42,43,44],"repetitions":3}` with actual values. One recorded run/seed is not evidence of statistical stability.

Optimization, including prediction/robust/multi-objective optimization, additionally needs a `solver` object with actual `name`, `version`, `status` (`optimal`, `feasible`, or `time_limit`), `problem_type` (`lp`, `mip`, `cp`, `nlp`, `global`, `heuristic`), `has_incumbent: true`, independently checked `feasibility_verified: true`, and a finite `objective`. MIP/global also requires finite `bound` and nonnegative `gap`. Keep exact native status in the validation artifact. A time limit is acceptable only with a usable feasible incumbent. Infeasible/unbounded/failed exploratory cases belong in history, not as the selected answer.

Inputs, used code/config, results and validation must exist. The validation protocol and baseline artifact must be explicit; an adequate baseline may be the selected model. Logs, this manifest, automatic audit reports and unchanged inputs/code cannot stand in for results. Fill `file_stamps` from the actual files as part of that execution, not later to silence a stale result. The empty example above intentionally cannot pass:

```python
# Run after exporting the real results and validation, before recording completion.
tracked = run["inputs"] + run["code"] + run["artifacts"] + run["validation"]["artifacts"]
run["file_stamps"] = {}
for relative in dict.fromkeys(tracked):
    stat = (project_root / relative).stat()
    run["file_stamps"][relative] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
```

Changed size/mtime stamps invalidate linkage even for rapid edits. Inputs/code after a run or outputs before it also trigger a stale-time finding (2-second filesystem tolerance for this extra timing check). These metadata checks are not tamper-proof integrity: intentionally preserved size/timestamps can conceal content changes. Do not modify timestamps/stamps to pass. Rerun or reconstruct an honest record from available evidence and disclose anything unrecoverable.

**Freeze order:** the auditor invalidates a selected run when any file listed in `run.code` changes, including `config/parameters.yaml` and including comment-only edits. Therefore finalize parameter-source annotations, comments and documentation for those files **before** the selected run, not after it. Once the model is frozen, do not touch any file listed in `run.code`; if a change is unavoidable, rerun and re-record instead of editing the stamps.

No whole-project hashing is performed. Only original inputs, key model files, final deliverables and explicitly integrity-checked downloads warrant optional hashes. Ordinary intermediates do not need repeated hashing.

## Result claim map

Keep one Markdown table at `docs/evidence_map.md` or the manifest's `canonical_directories.evidence` path:

| Claim ID | Question | Run ID | Paper claim | Source artifact | Metric/value | Conditions | Paper location | Verification |
|---|---|---|---|---|---|---|---|---|
| C-01 | 1 | q1-selected-run | Actual bounded result statement | `results/tables/q1.csv` | Actual metric/value | Actual split/seed/scenario | Actual section/table | unverified |

Replace the example, and use exact `verified`/`已核验` only after checking the actual value, definition, units, denominator and condition. An optional extra column headed `Verified by`/`核验人` records WHO did that check; when present the auditor requires one of `self-check`/`自查`, `independent-rerun`/`独立复算`, `team-member`/`队员核验`, so an assistant self-check cannot silently read as a teammate's review. Omitting the column changes nothing. `unverified`, `not verified`, `未核验` and partial substrings never pass. Each question needs at least one result claim; sources must be declared result/validation artifacts of that selected run. Additional columns are allowed. Escape literal pipes inside cells as `\|`; use one source path per row and separate rows for independently supported claims. Source-only facts/assumptions stay in intake notes rather than duplicating the entire paper here.

The tool verifies links and exact states, **not arbitrary arithmetic or the truth of a manually entered verified flag**. Derive percentages and headline values in canonical results, then independently reconcile them with the manuscript. Unexecuted methods and unresolved critical claims cannot be repaired merely by removing a placeholder word.

In the existing QA record distinguish assistant checks, independent calculation/rerun, and actual team-member human review. A verified arithmetic result or another Agent's approval is not evidence that a person completed the contest's required review. Do not fabricate review actors or client submission acknowledgments.

## Build and review records

`build_paper.py` resolves the declared LaTeX/PDF paths, uses a fresh build directory and checks process success, material log warnings and actual PDF parsing (pypdf or Poppler pdfinfo). It records project-local dependencies from TeX's `.fls` and bibliography declarations in `.aux`/`.bcf`, and saves a `.build.json` beside the PDF. Only an existing output with this tool's receipt may be replaced; otherwise choose a new `submission.pdf` path to preserve the old artifact. The receipt links source dependencies to the PDF by size/mtime, with `visual_review: pending`; it is never visual or numeric acceptance.

After building, inspect every rendered page and decisive number and record the conclusion in **`docs/qa_report.md`**. Rebuild if source/bibliography/figures change. Missing or changed build evidence cannot be replaced by an unrelated PDF elsewhere in the paper directory.

During editing, rebuild when dependencies change. Once final files have been frozen for an official submission digest, preserve them: CUMCM's distinct MD5 and file-upload windows are defined in [cumcm-official.md](cumcm-official.md). Local file linkage, mathematical review, team human review, and official submission acceptance are separate states.

## Auditor behavior

`--strict` exits 2 for BLOCKER, 1 for MAJOR, 0 when the implemented checks pass, and 3 for invalid input/report operations. Success status is **`STRUCTURE_CHECKS_PASSED`**, always with `review_required: true`. This does not certify mathematical correctness or permit submission.

Default text limits: 2 MB per file, 20 MB total, 5,000 files; adjust with `--max-file-bytes`, `--max-total-bytes`, `--max-files` only when useful. Read failures, malformed UTF-8 and limits are visible as incomplete scans. UTF-8 BOM is supported. The scanner caches text, excludes common source cache/build directories, and follows declared outputs rather than recursively reading all raw data/results. It does not execute project code.

Use `--report docs/structural_audit.md` for the machine report. Reports cannot overwrite protected inputs/code/evidence/submission/manual QA; an existing report is updated only if it carries the tool's ownership marker. Keep manual notes out of machine reports. No report argument means no project writes. A partial analysis task need not satisfy a final-submission contract; do not create a full project just to silence a submission audit.
