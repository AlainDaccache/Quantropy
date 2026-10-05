# Interactive Brokers and execution engineering

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Interactive Brokers is a plausible broad-market retail execution adapter. Selecting it requires a capability matrix for the actual account, region, permissions, instruments, order types, data subscriptions and installed gateway/API. TWS/Gateway and Web API have different session and integration behaviors; choose one initial path through a small proof of fit. Broker history is not a substitute for a survivorship-free historical research dataset. [Data documentation](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/introduction).

The order service needs a durable state machine: intent, risk approval, submitted/acknowledged, partially filled, filled, cancelled, rejected and unknown. Model cancel/replace races and corrections. Persist internal intent IDs, broker IDs and executions. An uncertain submit result is not permission to submit again blindly. Reconnect by recovering broker open orders/executions/positions and matching them to durable state. [Order reference](https://www.interactivebrokers.com/docs/tws-api/ref/order), [errors](https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes).

Add limit/market/stop/bracket policies, time-in-force, market hours, tick/lot validation, multi-leg constraints and execution quality analysis. Margin/commission previews inform a check but are estimates. [Order preview](https://www.interactivebrokers.com/docs/web-api/v1/endpoints/orders/preview-order-what-if-order). Account-level exposure includes manual trades and other strategies. Rate limits, pacing, authentication and reconnect procedures must be tested against current documentation and actual behavior.

Acceptance: disconnect after submit, duplicate/out-of-order callbacks, partial fills, crash/restart, expiry, manual trades and stale data drills. No duplicate economic order intent; discrepancies block automated progression. Start read-only, then replay and paper, then a tightly capped live instrument profile after explicit enablement. Broker paper fills are diagnostic, not validated market liquidity.

## Coverage checklist

- IBKR API choice and account capability matrix
- Instrument contract resolution
- Durable order intent and state machine
- Risk approval and order preview
- Market limit stop bracket policies
- Partial fills cancel replace race handling
- Duplicate and out-of-order callback handling
- Disconnect recovery and unknown submissions
- Broker positions orders executions reconciliation
- Pacing sessions entitlements and permissions
- Manual trade coexistence
- Execution quality and implementation shortfall
- Read-only paper and capped live profiles

## Research sources

- [IBKR-DATA](sources.md#ibkr-data)
- [IBKR-HISTORY](sources.md#ibkr-history)
- [IBKR-ORDER](sources.md#ibkr-order)
- [IBKR-WHATIF](sources.md#ibkr-whatif)
- [IBKR-ERRORS](sources.md#ibkr-errors)
- [IBKR-FLEX](sources.md#ibkr-flex)

[Knowledge base index](README.md)
