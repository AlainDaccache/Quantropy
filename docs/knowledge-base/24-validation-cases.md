# Independent worked validation cases

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

These are proposed fixtures, not passed tests. Use small transparent examples before large backtests.

1. Cash equity ledger: start with 1,000; buy 10 units at 50 and pay 1 fee; cash 499, marked position 500, equity 999. Sell at 55 with 1 fee; final cash/equity 1,048, net P&L 48. Missing marks must not erase the 10 units.
2. Initial drawdown: start equity 100; fall to 90 then recover to 95. Maximum drawdown is 10%, even if the return array starts with the loss and omits an explicit initial row.
3. External flow: 100 grows to 110, deposit 90, then portfolio grows 10% to 220. TWR is 21%; the deposit is not investment profit. MWR needs dated flows and its own convention.
4. Futures: buy one contract at 100 with multiplier 50, settle at 102. Variation margin is 100. Posted margin is collateral, not the purchase price. A later cash-settlement/revaluation event must not double-count the 100.
5. Dividend/split: two shares at 50 become four at 25 on a two-for-one split, preserving value. A cash dividend adds the declared cash while the market price is independently marked; avoid assuming a precise price response.
6. Causality: a filing with fiscal year end December 31 released March 1 cannot influence a February decision. Append a later year of prices; earlier features/orders must remain unchanged.
7. Costs: an entry and exit each charging 1 must book total cost 2 whether the exit is a stop, target, timeout or terminal liquidation.
8. Options: for a non-dividend European reference fixture with matching conventions, test put–call parity and numerical Greeks. American options require different bounds/inequalities, not unconditional European parity.
9. Curve: discount a known coupon schedule by a supplied curve, then reprice the bootstrap calibration instruments within declared tolerances.
10. Recovery: submit an intent, drop the connection before acknowledgement, recover an existing broker order. Do not create a duplicate intent to make the log look complete.

Extend fixtures to nonstandard calendars, FX conversion, tax lots, bankruptcies, partial fills, delivery notices and stress liquidity. Expected outputs must be independently derived and reviewed before coding.

## Coverage checklist

- Independent cash-equity fixture
- Initial-equity drawdown fixture
- External-flow TWR MWR fixture
- Futures settlement and margin fixture
- Split dividend and correction fixtures
- Availability and prefix-causality fixture
- Every-exit round-trip-cost fixture
- Pricing parity bounds and Greek fixtures
- Curve bootstrap repricing fixture
- Uncertain-submit recovery fixture

## Research sources

- [CME-CASH](sources.md#cme-cash)
- [GIPS](sources.md#gips)
- [OIC-EXERCISE](sources.md#oic-exercise)
- [LEAN-LIVE](sources.md#lean-live)

[Knowledge base index](README.md)
