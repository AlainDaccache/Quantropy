# Causal historical replay and evaluation protocols

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [13-factors](13-factors.md).

## Data and event contract

Each fact records observation interval, first publication timestamp, vendor availability, revision identifier and ingestion time. An as-of query at decision time uses only versions available by then. A historical universe includes delisted and inactive securities using eligibility known at that time. Keep original tradable prices, adjusted research views and corporate-action events separate.

Process events in declared causal order: market observation; available information update; signal/decision; order submission/latency; eligible fill; trade ledger; funding/margin; corporate actions/settlement; valuation. Two events at one timestamp need an explicit tie-break. A bar close can generate a next-event order; same-close fill needs a justified earlier information/order mechanism. Unknown intrabar paths make simultaneous stops/targets ambiguous.

## Evaluation procedure

Reserve a chronological final holdout before method selection. Fit all feature transforms and hyperparameters on training information. Walk-forward expands or rolls the training window, then tests later periods without reuse. For label intervals [start_i,end_i], remove training observations whose information spans intersect test spans; additional embargo is a specified buffer for residual leakage/dependence. Combinatorial splits, embargo length and final holdout purpose are separate design choices.

Example label A spans days 1–5 and test label B spans 4–6: A must be excluded from training even if its start precedes the test. A feature published on day 7 must not enter a decision on day 6. Prefix causality checks rerun the pipeline truncated at a date and require decisions up to that date to match the full replay, except deliberately revised retrospective reporting.

Model fee schedules, spread, participation/impact, borrow availability, funding, margin, expiry/roll and capacity. A stop crossed by a price gap fills at a modeled reachable price, not automatically its trigger. If a daily bar touches both target and stop, report path scenarios/bounds or use finer data; do not select the favorable order. Forced timeout and terminal liquidation incur their costs.

Record every attempted variation. Report net performance, exposure, turnover, uncertainty and stability across regimes/universes. A strategy selected after repeated holdout viewing no longer has a pristine holdout. Paper/live comparison tests event timing and operational realism; it cannot prove an expected alpha persists.

## Evidence boundary

Supporting source map: [OVERFIT](../sources.md#overfit), [SKLEARN](../sources.md#sklearn), [LEAN-FILLS](../sources.md#lean-fills). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
