# Backtesting and realistic simulation

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Use two complementary levels: fast vectorized analysis to reject weak ideas and event-based simulation to test tradability, lifecycle and accounting. Shared strategy code and contracts should reduce divergence across simulation, replay, paper and live; execution environments still differ. [LEAN reconciliation](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/reconciliation).

Specify event ordering: data availability, signal calculation, decision, risk check, order arrival, fills, fees, settlement and marking. Same-bar execution requires evidence of availability; bar high/low does not reveal intrabar order. Ambiguous stop/limit/bracket outcomes need lower-resolution data or conservative ranges, not favorable assumptions. Touching a limit is not guaranteed execution.

Model partial fills, spread, queue/latency assumptions, impact, commissions, taxes/fees, financing, borrow availability/cost, dividends, corporate actions, futures settlement/rolls, option exercise and FX. Unknown costs must be flagged and stress-tested. Mark holdings with a declared missing/stale-price policy; missing data never makes a position disappear. [Fill models](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/trade-fills/key-concepts).

Return accounting begins with initial equity. Include cash distributions and external flows, separate realized/unrealized P&L and costs, and retain trades/order events for attribution. A fast simulator may simplify details but must disclose its fidelity and block unsupported strategies from graduation.

Acceptance: independently computed small scenarios, cash/position conservation, exact round-trip cost, cancelled/rejected/partial orders, expiry/assignment/delivery, initial-loss drawdown and prefix causality. Compare engine output with an independent reference and paper/live telemetry. A successful backtest is evidence conditional on the data/model, not proof of future performance.

## Coverage checklist

- Vectorized exploratory backtests
- Event-driven order and lifecycle simulation
- Causal event ordering and signal timing
- OHLC intrabar ambiguity policies
- Spreads slippage impact and queue models
- Commissions financing borrow and fees
- Partial fills stops limits brackets
- Corporate actions settlement rolls exercise
- Marking missing data and stale-price policies
- Independent accounting and return reconciliation
- Capacity and execution sensitivity
- Replay paper and live comparison

## Research sources

- [LEAN](sources.md#lean)
- [LEAN-FILLS](sources.md#lean-fills)
- [LEAN-LIVE](sources.md#lean-live)
- [OVERFIT](sources.md#overfit)

[Knowledge base index](README.md)
