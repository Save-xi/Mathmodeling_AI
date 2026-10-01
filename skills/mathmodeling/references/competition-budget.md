# Contest budget and stop conditions

Use for a full contest build or a task with a deadline. Record the real deadline/time zone and team/compute capacity. This 72-hour table is a planning example, not the rule for every contest. Scale it to the time actually remaining; allow rest and handoffs for human teammates.

For 2026 CUMCM, the verified contest interval is **74 hours**. The MD5 deadline and later file-upload window are different; use [cumcm-official.md](cumcm-official.md). Upload time after the contest is not extra modeling time. Work backward from the content/digest deadline and reserve time for the official client.

| Elapsed wall time | Primary outcome | Exit/freeze |
|---|---|---|
| 0–6 h | Sources, data, question contract and information boundaries | Definitions and critical unknowns visible |
| 6–18 h | Runnable baseline for every requested question | Results and initial validation; paper/evidence begins alongside code |
| 18–32 h | Defect-driven improvements only | One primary enhancement at a time; revert if unsupported |
| 32–42 h | Validation, sensitivity, decision replay | Freeze model route when evidence is sufficient |
| 42–44 h | Delivery rehearsal: run the full build and structural audit once | Clear every LaTeX layout warning now, ~30 h before the deadline, not in the final hours |
| 44–60 h | Complete paper, tables/figures, limitations | Important numbers linked to canonical outputs |
| 60–68 h | Rerun, numeric reconciliation, PDF/log/visual QA | Freeze values and submission version |
| 68–72 h | Four manual submission checks—page limit, anonymity in the text, PDF document properties/metadata, appendix source-code completeness—then file/package limits and submission buffer | Fix blockers only; no new model or environment |

## Operational limits

Reserve validation, writing, rerun and submission time before exploration. A reviewable baseline and a narrower honest answer outrank an unfinished ambitious route.

- Prepare the broad literature/algorithm anchors before the contest. During the contest, start with offline matching and only targeted gap checks: normally **10–15 minutes per primary route, at most 30 minutes for the initial selected routes**, or zero when already covered. Allow one focused follow-up for a material unknown. A genuinely uncovered problem can justify a larger explicit research budget, but no automatic two-hour survey. A **2-hour first-prototype cap** is a starting example; scale it to the remaining time and preserve delivery reserves.
- Count download/install, data generation, tuning, training, solver calls, ablation and debugging. First run a small end-to-end example and measure peak memory and runtime. Unknown hardware fit is not a pass.
- Set a finite trial/evaluation cap appropriate to the model. Stop feature engineering after the exploration checkpoint. The gain threshold is task utility or reproducible uncertainty, not a universal percentage.
- Baseline may equal selected model and fallback. A fallback can be a smaller instance, shorter horizon, simpler policy or last verified baseline; it need not be a third pipeline.

Stop model expansion when the baseline meets the declared quality/validation criteria with no worthwhile supported gap, or when gain is below the practical threshold or repeat-run/split variation, complexity weakens feasibility/interpretation, resources remain unavailable at the prototype cap, or full validation and writing no longer fit. For an explicit high-award target, perform one bounded [quality review](competition-excellence.md) before declaring the correct baseline sufficient. Strengthen interpretation or evidence where valuable; do not require another model.

After route freeze, change models only to fix material errors. Identify which outputs/claims need rerunning and rechecking. Preserve the last verified outputs until the correction passes; never combine an old PDF/result with new code silently. If a blocker remains at the deadline, narrow scope/claims and disclose it.

Keep deadline, remaining hours, baseline status, trial/solver cap, checkpoint, model freeze, delivery reserve and fallback in a short section of the existing contract. Update at meaningful stage changes, not per tool call. Do not generate a file per action or call an expensive specialist for routine formatting.

## Preparation and topic choice

Before the contest, use a short past-problem rehearsal to check the actual environment, solver/license, raw-data reading, one result, PDF build and independent rerun. A 2–4 hour targeted rehearsal is a starting example, not a mandatory full old-paper reproduction. Record the bottleneck and fallback, and ensure teammates can explain the core calculation. Avoid last-minute environment replacement.

For the few algorithm anchors actually being prepared, also front-load dependency/license checks, version pinning, necessary offline weights and representative synthetic/past-data smoke tests within the authorized scope. Their generic readiness does not require the unpublished contest statement. During the contest recheck actual input shapes, budget and task results; do not postpone all setup to that stage. A read-only preparation request leaves those executions pending, rather than making them inherently contest-time work.

Only if the topic is undecided, compare a few eligible questions within the initial intake budget: data/definition clarity, team understanding, baseline feasibility, validation access and total delivery cost. Do not predict award odds from topic popularity or automatically prefer a topic letter. Once the user selected a problem, continue it; changing topic needs a material feasibility reason. Match roles and handoff times to actual available people, rather than assuming three people or three agents always exist.
