# Execution, event state and live reconciliation

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [14-backtesting](14-backtesting.md); [19-treasury-public](19-treasury-public.md).

## Domain records

Intent identifies desired exposure and decision time. Order identifies broker/venue instruction and allowed quantity/price/time. Execution identifies an actual trade and economic quantity/price/fee. Position and cash are ledger results, not values to infer from order status alone. A cancellation request can race a fill; “cancel sent” is not evidence of zero remaining exposure.

Use stable client intent IDs and broker order/execution IDs. Record submissions, acknowledgments, partial fills, modifications, cancellations, rejections, busts and corrections as events with ingestion and effective timestamps. Economic processing must be idempotent by the appropriate event/version key. Order status transitions and execution records can arrive out of order; reconcile rather than enforcing an imaginary perfectly ordered transport.

## Failure procedure

On disconnect or an ambiguous submit response, stop duplicate submission for that intent; query/reconcile open orders, recent executions and positions using the broker's available interfaces. Classify unknown state explicitly. Resume only after identity/quantity/cash reconcile or apply a declared exception workflow. Compare ledger to broker holdings/cash, separately accounting for settlement, corporate actions, expiry/exercise, currency and corrections.

Example intent buys 10; fills arrive 4 then 6. Duplicate receipt of the first fill still results in total 10, not 14. A cancel submitted after the first fill may leave total anywhere from 4 to 10 until confirmation/reconciliation. Restarting the client must not create a second buy-10 order simply because local acknowledgment was lost.

## Execution quality and controls

Choose decision/arrival reference price and measure realized slippage, fees and opportunity cost for unfilled intent. Bar-based fill models must address spread, gaps, queue priority and participation. A market order's final price is unknown at decision time; a limit may never fill. Price collars, order/notional limits, stale-data checks, cash/margin limits and an explicit emergency control are release requirements.

Broker paper behavior and market-data entitlements are not guaranteed live equivalence. Validate current API semantics against dated documentation and sandbox fixtures before enabling live orders. This knowledge contract specifies concepts and failure behavior; it neither connects an account nor authorizes trading.

## Evidence boundary

Supporting source map: [IBKR-ORDER](../sources.md#ibkr-order), [IBKR-ERRORS](../sources.md#ibkr-errors), [LEAN-LIVE](../sources.md#lean-live), [PFMI](../sources.md#pfmi). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
