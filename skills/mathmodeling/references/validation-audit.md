# Validation, robustness, and submission audit

Validation is an evidence chain, not a final paragraph added after favorable results.

## Correctness ladder

Audit in this order:

1. **Source:** original fields, units, legal choices, time/space definitions, and output requirements were read correctly.
2. **Mathematics:** formulas, indices, domains, signs, boundary cases, dimensions, and linearizations match the model contract.
3. **Implementation:** code maps to each equation/constraint; toy cases and targeted tests isolate key logic.
4. **Numerics:** convergence, tolerances, status, conditioning, bounds/gap, runtime, and random seeds are recorded.
5. **Empirics:** baseline comparison, out-of-sample/backtest, residuals, calibration, or simulation intervals fit the task.
6. **Claims:** every important conclusion is no stronger than the evidence and uses the same definition/denominator.
7. **Reproducibility:** inputs, parameter sources, environment, entrypoints, canonical outputs, and run logs are recoverable.

Do not skip an earlier rung because a later metric looks good.

## Formula and implementation checks

- Re-derive one representative formula independently and hand-calculate a small case.
- Check units on every sum/product and objective term; normalize only with recorded scale direction and denominator.
- Test zero, one-item, all-capacity, infeasible, extreme, and symmetry cases where meaningful.
- Map every constraint family to code and record expected row/variable counts for a toy instance.
- Verify objective direction and post-processing conventions. A negative solver objective relabeled as profit is a common silent error.
- For relaxations or linearizations, state the original relation, auxiliary variables, valid bounds, and exactness conditions.

## Solver evidence

For each optimization run record:

- solver/version, model size, time/memory limit, tolerances, and hardware if relevant;
- termination/status, feasibility checks, objective value, runtime, incumbent and bound;
- MIP or global optimality gap when applicable;
- any dropped constraints, fallback heuristic, repair, or manual intervention.

Independently recompute the objective and major constraints from exported decisions. `OPTIMAL` is not proof that the intended model was encoded.

Audit the actual reported decision after rounding, clipping, repair, aggregation or rescheduling. Preserve the raw solver output and label any relaxation/local/heuristic bound separately; its objective or gap cannot automatically be assigned to the transformed decision. A second algorithm solving the same equations is useful numerical cross-checking, but does not independently establish that those equations model the original task correctly.

## Model adequacy and strongest-claim challenge

For each conclusion-critical assumption, state the consequence, available justification and a feasible way it could fail. Test a plausible alternative formulation when it could change the answer; favorable fitting error does not identify a mechanism. Separate data/measurement uncertainty, discretization or solver error, Monte Carlo error and structural model discrepancy when they affect the conclusion. Do not run every possible diagnosis merely to populate a section.

Check the quantifier in the strongest claim: a grid maximum, local optimum, earliest sampled crossing or successful finite simulation is not automatically a global maximum, first event or universal guarantee. Derive a valid bound, use an appropriate convergence/event/coverage argument, or narrow the statement. Prioritize a small legal counterexample capable of falsifying the central claim over another redundant favorable example.

## Validation by model type

- **Forecast/classification:** leakage-safe backtest, naive baseline, residual/error slices, calibration, and uncertainty.
- **Ranking/evaluation:** weight/normalization sensitivity, rank correlation, leave-one-indicator-out, and dominance sanity checks.
- **Optimization:** feasibility recomputation, relaxation/lower bound, baseline policy, perturbations, and extreme-case solutions.
- **Simulation:** seeds, warm-up, repetitions, confidence intervals, event traces, conservation checks, and convergence.
- **ODE/PDE/inverse:** synthetic recovery, residuals, identifiability, initial/boundary-condition checks, and discretization convergence.
- **Network:** edge/source construction audit, connectivity, alternative definitions, and perturbation/removal stability.

## Robustness menu

Choose tests tied to the main conclusion:

- parameter sweeps around uncertain values and threshold/breakpoint analysis;
- scenario stress tests, including rare adverse combinations;
- out-of-sample or rolling-window validation;
- ablations for each claimed module contribution;
- alternative metrics/normalizations and baseline policies;
- random-seed and sampling stability;
- solver tolerance, time-limit, and scenario-count sensitivity;
- data-removal, outlier, and missingness perturbations.

Define the test, metric, and acceptable change before seeing the result. If a conclusion flips, narrow the claim instead of hiding the instability.

## Task-dependent checks for all model families

Apply each relevant row according to the data and claim, including for classical models. These are not conditional on an Innovation Scan. Skip an irrelevant test with a reason; do not mechanically run the whole menu.

| Risk | Required audit |
|---|---|
| Data leakage | Freeze deployment time and entity boundaries; audit windowing, normalization, graph construction, decomposition, pretraining overlap, target-derived features, and simulation/observation reuse. |
| Overfitting/small-sample instability | Compare learning curves and simpler baselines; use nested/rolling validation where appropriate, repeated seeds, uncertainty across splits, and complexity ablation. |
| Distribution shift | Hold out time, entity, region, parameter regime, geometry, resolution, or policy environment matching the claimed use; do not infer OOD ability from IID test error. |
| Uncertainty calibration | Report coverage, interval width/sharpness, probability calibration and tail behavior on unseen data; propagate uncertainty into downstream decisions. |
| Forecast object validity | Match validation to the delivered object: point error, marginal interval coverage, multi-horizon joint coverage, or trajectory/path-event calibration. Do not infer cumulative exceedance, peak, or simultaneous-failure probabilities from marginal intervals alone. |
| Physical consistency | Check initial/boundary conditions, dimensions, conservation/invariants, residual distribution, numerical convergence and long-horizon stability, not physics loss alone. |
| Physical calibration identifiability | When estimating physical parameters plus learned discrepancy, run synthetic recovery and alternative-prior/architecture tests to show the two branches are not arbitrarily exchanging signal; hold out unseen realizations if amortization is claimed. |
| Causal identification | State DAG/SCM, timing, treatment, outcome, estimand, overlap and confounding assumptions; run balance, placebo/negative-control or sensitivity checks where possible. Predictive accuracy is not causal evidence. |
| Partial identification | If only bounds are identified, audit every assumption producing the bounds, report bound width and sensitivity, and do not replace the interval with a midpoint causal estimate. |
| Optimization feasibility | Recompute all hard constraints and objective from exported decisions; report fallback/repair, bounds/gap, policy meaning and performance under prediction error. |
| Learning-assisted decisions | Report decision regret/tail regret when relevant, feasible rate, oracle/solver calls, training plus solve wall-clock cost, and the exact feasibility repair. A prediction metric alone cannot validate decision-focused learning. |
| Randomness/hyperparameters | Record seeds and search budget; report repeated-run dispersion and sensitivity to influential hyperparameters rather than the best run only. |
| Module contribution | `A` vs `A+B` tests the added module; `A`, `A+B`, `A+B+C` only tests sequential gains. Independent B/C or interaction claims need matching controls such as `A+C`; if unaffordable, narrow the claim. |
| Baseline and cost | Use the same split/scenarios/metrics; report accuracy or decision gain together with runtime, memory/compute, dependency complexity and prototype/training cost. |
| Amortization and pretrained resources | Report weights, license, offline availability, dependency/hardware fit, one-run training cost, per-query cost and break-even number of repeated instances; a train-once surrogate is not a speedup for a single solve unless total cost supports it. |

Reject or downgrade a complex model if it does not materially improve at least one task-critical dimension—accuracy, robustness, interpretability, runtime, physical consistency, uncertainty quality, or decision quality—without unacceptable loss elsewhere. A fresh paper, public checkpoint, or successful training run is not validation of this task.

## Split, resampling and uncertainty protocol

1. Define the independent unit and intended deployment before splitting. For IID classification, stratification may preserve class proportions; repeated entities require grouped CV when claiming new-entity performance. Panel prediction may need both time and group holdouts; known-entity future prediction need not exclude all known entities.
2. For forecasting, use rolling origins or forward temporal blocks with the same forecast horizon and explicit refit/calibration policy. Audit overlapping label windows, data revision delays and any needed gap/embargo. Generic blocked CV does not authorize using future observations to predict past origins.
3. For spatial generalization, hold out regions/blocks and, when dependence warrants it, a buffer. Choose block size using dependence and deployment scale, not the split with the best score. Audit graph construction inside the same information boundary.
4. Fit preprocessing, imputation, decomposition, feature selection, hyperparameters and classification thresholds only within training/validation. Use nested selection when useful for small-sample comparison; never reuse the final test to choose features, modules or risk parameters.
5. Bootstrap the independent unit: individual units for an IID design, groups for grouped data, temporal blocks for dependent series. State resampling unit, block choice, repetitions and interval interpretation. More resamples do not create more independent observations.
6. Distinguish parameter confidence/credible intervals from predictive intervals, Monte Carlo error and scenario ranges. Assess predictive coverage/width/calibration on unseen data; simultaneous/path guarantees require the appropriate joint object and assumptions, not independent marginal bands.

Inspect residual bias, autocorrelation, heteroskedasticity and failure slices where relevant. Check learning curves/simpler models for overfitting, influential hyperparameters, repeat seeds, data perturbations and at least one plausible alternative specification when the main conclusion depends on a disputed assumption. A stable objective can hide unstable actions: compare decision variables, rank/selection changes and constraint margins.

Statistical significance and practical value are separate. Report effect size, interval, independent sample count and the actual test definition when a significance claim is made; dependence and multiple comparisons must match the design. Do not add arbitrary p values to optimization outputs or call a tiny statistically detectable change practically important.

## Prediction followed by optimization

Use this for ordinary forecast + LP/MILP/policy pipelines as well as learned decisions:

1. At each held-out historical decision time, fit the forecast, transforms and calibration using only available history.
2. Generate predictions or calibrated scenarios, preserving important cross-variable/time dependence and tail behavior. Select risk parameters using validation, not the final replay outcomes.
3. Solve and freeze the action without reading the future realization. An oracle using future truth is an evaluation bound only, never a deployable comparator.
4. Evaluate the action on the subsequently realized inputs: objective/loss, constraint violations, regret when meaningful, tail loss and service level. Independently recompute hard constraints and objective from exported actions.
5. Compare baseline and enhancement on identical origins/information/constraints, including total forecast/calibration/solve cost. Stress correlated errors and check action stability. If only simulation is available, call the result simulation evidence and state fidelity limits.

Lower RMSE need not improve decisions. For true costs `(10,11)`, forecast `(9,10)` has RMSE 1 and chooses the cheaper action; `(10.6,10.4)` has RMSE 0.6 and chooses the costlier action. This illustrative calculation motivates decision evaluation; it is not an empirical contest result.

## Numeric and claim consistency

- Generate tables/figures from canonical result files; avoid hand-copying numbers into the paper.
- Cross-check abstract, body, tables, figure labels, captions, conclusions, and appendix for the same metric definition, sample/scenario count, and rounding.
- Maintain `docs/evidence_map.md` with claim, source artifact, exact condition, value, paper location, and verification status.
- Separate observations, calibration simulations, posterior probabilities, and scenario results. They are not interchangeable.
- Preserve concise run records linking the selected per-question execution, inputs/code, outputs, validation and claims; see [project-evidence.md](project-evidence.md). Do not hash ordinary intermediates repeatedly. Hash only original inputs, key models, final deliverables or downloads with an actual integrity need; version/run linkage is otherwise sufficient.

## Independent review pattern

When an independent model/agent review is requested, let the primary reviewer freeze its result first. Give the second reviewer the original problem, data contract, equations, code, and canonical outputs, and ask it to re-derive or falsify critical steps. Do not have two reviewers merely continue the same prose. Compare only after both reviews are frozen.

## Severity

`BLOCKER`/`MAJOR`/`MINOR` are defined once in the main skill's severity gate; use that definition rather than a second copy here.

The bundled `audit_project.py` checks declared structure/run/claim links, explicit states and readable artifacts only. `STRUCTURE_CHECKS_PASSED` still requires independent equation review, actual reruns, output inspection and domain judgment. Automated reports go to `docs/structural_audit.md`; preserve manual numerical and visual acceptance in `docs/qa_report.md`.
