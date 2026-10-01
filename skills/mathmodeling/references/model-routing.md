# Model-family routing

Choose from the problem contract, data volume, required evidence, runtime, and contest deadline. Do not select a method because it sounds advanced.

## Candidate pattern

For each question retain these roles; they may share one implementation, and an adequate baseline can remain the final model:

1. **Baseline:** transparent, fast, and hard to misuse; establishes whether complexity adds value.
2. **Main model:** best balance of mechanism fidelity, data support, solvability, and explainability.
3. **Backup:** viable if assumptions, data, packages, or solver performance defeat the main model.

Compare them under the same data split, scenario set, metric definition, constraints, and runtime budget. Mark non-comparable numbers instead of ranking them.

This file owns the classic route. During selection, match the prepared `$mathmodeling-frontier` anchors to the task, independent data units, horizon, constraints and resource envelope; this offline lookup does not trigger web research or require replacing the baseline. Preparation and targeted research follow [innovation-routing.md](innovation-routing.md). Do not replace a suitable linear model, ARIMA, PCA, LP/MILP or numerical solver merely because an anchor includes a newer method.

## Routing table

| Task | Baseline | Warranted candidates | Required evidence / rejection boundary |
|---|---|---|---|
| Regression | mean/median, linear/ridge | transformations, low-degree splines/GAM, small tree ensembles, constrained regression | independent units, residuals, holdout gain; reject unstable flexibility or unsupported extrapolation |
| Classification | majority/class-prior, logistic | regularized linear/SVM, trees/boosting | minority-event count, cost-sensitive metrics, threshold selected inside validation, probability calibration |
| Clustering | scaled k-means and no-cluster description | hierarchical/density methods if distance and shape justify them | resampling/scaling stability and task meaning; do not invent labels or use supervised accuracy on unlabeled clusters |
| Time series | naive/seasonal naive, ETS, simple ARIMA/state space | dynamic regression, regularized lags, modest tree models | rolling origins and matching horizon, residual autocorrelation, known future covariates; reject leakage/too few cycles |
| Panel/repeated measures | pooled regularized model, entity/time summaries | fixed effects, justified random/hierarchical effects, shared state space | time and entity deployment target; group/time holdouts; fitted entity effects cannot directly solve new-entity prediction; with short T (roughly T<10) a lagged dependent variable under fixed effects carries Nickell bias, so prefer pooled/summary regression with group and time holdouts |
| Graph/network | shortest path/flow/matching or no-graph predictor | reliability/community/temporal network, simple spatial-lag models | distinguish graph optimization from graph prediction; reject arbitrary/future-derived edges or no gain over fixed/no graph |
| Optimization | feasible greedy/native heuristic plus useful relaxation | LP/MILP, network flow, DP, CP, convex/NLP or justified global methods | feasible incumbent, status, bounds/gap, installed/license fit and total runtime; no usable feasible output means reject |
| Multi-objective | meaningful single-objective anchors | epsilon-constraint, lexicographic priorities, bounded Pareto exploration | scale/preference sensitivity, nondominance and infeasible regions; weighted sums can miss nonconvex frontiers |
| Causal/policy effects | descriptive association plus DAG/timing/estimand | adjustment, matching/weighting, DiD, IV or RD only with a matching identifying design | confounding/overlap, parallel trends/instrument/cutoff assumptions and interference; without identification retain association/scenarios or justified bounds |
| Robust/stochastic decisions | nominal solution and interpretable stress scenarios | calibrated bounded robust model, stochastic programming, chance constraints, CVaR | independent calibration, unseen stress cases, tail sample and conservatism cost; no distribution/set justification means downgrade |
| Uncertainty quantification | residual distribution and sensitivity | correct-unit bootstrap, low-dimensional Bayes/GP, quantile/calibrated intervals | distinguish parameter/prediction and marginal/joint intervals; dependent rows cannot simply be IID-resampled |
| Prediction + optimization | simple forecast plus feasible decision | calibrated scenarios, robust/stochastic layer, modest residual correction | historical decision replay, realized objective/violations/regret; lower prediction error alone is insufficient |
| Simulation | deterministic balance, small traceable DES/Monte Carlo | mechanistic DES/agent simulation when interactions matter | calibration separate from policy evaluation, warm-up, stopping precision, replications, invariants and fidelity |
| Dynamics/inverse | balance, numerical ODE/PDE, least squares/system identification | constrained/regularized inverse, low-dimensional Bayesian methods | synthetic recovery, identifiability, boundary conditions and convergence; separate parameter error from structural discrepancy |
| Compartmental/epidemic dynamics | curve fit plus a small SIR/SEIR balance | age/contact-structured compartments, time-varying transmission, explicit reporting/delay layer | R0 and initial susceptible S(0) are typically not separately identifiable from a single reported-case curve; freeze reporting-rate and delay definitions before fitting; fit quality does not identify the mechanism |
| Queueing/service systems | M/M/c or M/M/c/K analytic formulas | priority/blocking disciplines, general service times, discrete-event simulation | arrival-process stationarity and independence checks, utilisation below 1, simulation cross-check; reject analytic formulas when arrivals are clearly non-stationary or the discipline differs |
| Evaluation/ranking | defensible weighted score/rank sum | TOPSIS, entropy/CRITIC, PCA/factor, AHP with defensible judgments | scale direction, rank/weight sensitivity; observed variance is not automatically decision importance |
| Legacy Chinese-contest families | the modern row matching the task (time series, evaluation/ranking) | GM(1,1) grey forecast and fuzzy comprehensive evaluation, as explicitly downgraded reference models | downgrade openly instead of omitting silently; GM(1,1) only when the series is short (roughly n<10) and near-exponential, and only compared with ARIMA/linear extrapolation under the same protocol; fuzzy comprehensive evaluation requires a sourced membership function, otherwise it equals arbitrary weighting and inherits the Evaluation/ranking sensitivity requirements. AHP belongs to the Evaluation/ranking row above and is admissible on that row's terms—documented pairwise judgments with a consistency check—so do not treat it as downgraded here; the shared failure mode across this family is an undocumented weight, not the method's age |

## Optimization details

- Define indices, domains, units, objective sign, constraint sense, and information timing before choosing a solver.
- LP/MILP/CP tools may include Gurobi, OR-Tools, Pyomo, PuLP, CVXPY, or SciPy, but inspect what is actually installed and licensed.
- Use exact optimization as the decision layer when the instance supports it. ML/GNN/RL may forecast inputs, generate scenarios, or warm-start; do not replace a verifiable small/medium exact model without evidence.
- For epsilon-constraint analysis, first solve meaningful single-objective anchors, choose an interpretable epsilon grid, and report infeasible regions rather than hiding them.
- If a time limit is reached, report incumbent, bound, gap, and whether the decision remains usable.
- When a MILP will not solve inside the available time, degrade in this order: tighten bounds or fix variables from problem structure; relax integrality and round with an explicit feasibility repair; shrink the instance (fewer periods or entities) and state the scope reduction; accept a time-limited incumbent and report bound and gap. Report every fallback actually used; an unreported shrink is a scope change, not a solution.
- Under parameter perturbations or alternative optima, inspect selected actions and constraint margins as well as objective stability. Count preprocessing, tuning and solver calls in the same candidate budget.

## Prediction and machine learning

- Split by the deployment information boundary; never let future, target-derived, or repeated-entity information leak.
- Tune only inside training data. Keep a final untouched test or rolling evaluation when data permits.
- Compare against naive and simple statistical baselines. Report error distributions, not only one mean metric.
- Calibrate probabilities/intervals when decisions depend on them. Explain how prediction error propagates downstream.
- Match validation to known-entity future, new-entity or new-region deployment. Use the split and historical decision-replay protocols in [validation-audit.md](validation-audit.md), including for classical models. Select classification thresholds inside validation; evaluate clustering stability rather than fabricated supervised metrics.

## Simulation and dynamics

- Separate model calibration from policy evaluation.
- Establish warm-up, horizon, event logic, numerical step size, replications, and stopping rules before reading favorable results.
- Validate conservation laws, invariants, limiting cases, and convergence as step size or replication count changes.

## Uncertainty routes

- **Sensitivity:** one-at-a-time/local effects for interpretation.
- **Scenario analysis:** discrete plausible futures with documented probabilities or equal-weight rationale.
- **Robust optimization:** protection against bounded uncertainty; report conservatism cost.
- **Chance constraints:** only with a defensible distribution/calibration.
- **CVaR/tail risk:** define tail direction, confidence level, scenario weights, and economic meaning.
- **Bootstrap/Bayesian intervals:** when inferential uncertainty, rather than decision uncertainty, is central.

Prefer a model whose assumptions can be audited and whose outputs can become paper evidence within the available time.

## Conditional research handoff

Before a contest, prepare sourced method alternatives for the relevant families. During the contest, use the selected anchor's narrow gap queries only when task conditions are missing, contradictory or materially changed; an explicit latest-now request also requires this targeted refresh. A structural keyword or ordinary citation request does not justify a full new survey. Adoption still needs a credible baseline and local validation. Never map time series to Transformer, graphs to GNN, PDEs to PINN, control to RL or optimization to animal metaheuristics automatically.
