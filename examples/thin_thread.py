"""T1 — the thin thread: one signal through the whole spine.

Backtest mode (default, offline after first fetch):
    python examples/thin_thread.py
        data (stooq -> pinned snapshot) -> MA-cross signal -> vol-target sizing ->
        risk limits -> event-driven backtest through SimulatedVenue -> summary.

Live-paper mode (requires TWS/IB Gateway running, API enabled, port 7497):
    python examples/thin_thread.py --live
        computes TODAY's target through the *identical* decision path, then routes
        the order through IBKRVenue instead of SimulatedVenue — the same seam,
        which is the whole point (MASTER_SPEC P6).

Every number printed by backtest mode is raw and [backtest]-tagged; nothing here
claims alpha — T1 proves plumbing (spec §6, T1).
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

from quantropy.backtest import BacktestConfig, RiskLimits, SimulatedVenue, run_backtest
from quantropy.data import AssetClass, Instrument, SnapshotStore
from quantropy.evaluation import summary
from quantropy.portfolio import VolatilityTarget
from quantropy.research import MovingAverageCross

SYMBOL = "SPY"
SNAPSHOT_ID = "t1-spy-daily"
STORE_ROOT = os.path.join(os.path.dirname(__file__), "..", "data")

INSTRUMENT = Instrument(SYMBOL, AssetClass.ETF)
SIGNAL = MovingAverageCross(fast=20, slow=100)
SIZER = VolatilityTarget(target_vol=0.10, lookback=63, max_leverage=2.0)
LIMITS = RiskLimits(max_leverage=2.0, max_drawdown=0.20)


def load_prices() -> pd.Series:
    """Snapshot-pinned closes: fetch once from stooq, then read offline forever."""
    store = SnapshotStore(STORE_ROOT)
    if SNAPSHOT_ID not in store.snapshots():
        print(f"fetching {SYMBOL} from yahoo (one-time) -> snapshot {SNAPSHOT_ID!r} ...")
        from quantropy.data.providers import use_system_trust
        from quantropy.data.providers.yahoo import fetch_daily

        use_system_trust()  # harmless where certifi works; required where it doesn't
        frames = fetch_daily([SYMBOL])
        store.write(SNAPSHOT_ID, {SYMBOL: frames[SYMBOL]}, note="T1 thin thread (yahoo)")
    # AdjClose = total-return-ish series (splits+dividends) — the right choice for
    # a signal on an ETF; the raw Close is in the snapshot too (Curriculum I.6).
    closes = store.read(SNAPSHOT_ID, SYMBOL)["AdjClose"]
    return closes.loc["2015-01-01":]


def backtest(prices: pd.Series) -> None:
    venue = SimulatedVenue(slippage_bps=1.0, cost_bps=1.0, commission=0.0)
    result = run_backtest(
        prices,
        SIGNAL,
        SIZER,
        INSTRUMENT,
        limits=LIMITS,
        venue=venue,
        config=BacktestConfig(initial_cash=100_000.0, snapshot_id=SNAPSHOT_ID),
    )
    stats = summary(result.equity)
    print(f"\n[backtest] {SYMBOL} MA({SIGNAL.fast}/{SIGNAL.slow}), vol-target 10%, "
          f"snapshot={SNAPSHOT_ID!r}")
    print(f"  bars={stats['bars']}  CAGR={stats['cagr']:.2%}  vol={stats['ann_vol']:.2%}  "
          f"sharpe_raw={stats['sharpe_raw']:.2f}  maxDD={stats['max_drawdown']:.2%}")
    print(f"  costs paid: ${result.total_costs:,.0f}   kill-switch tripped: {result.killed}")
    print("  (raw, undeflated, toy signal — the point is the plumbing, not the alpha)")


def live_paper(prices: pd.Series) -> None:
    """Identical decision path; the venue is the only thing that changes."""
    from quantropy.backtest.venue import Order
    from quantropy.live import IBKRVenue

    raw = SIGNAL.target(prices)
    weight = LIMITS.apply(SIZER.scale(raw, prices), equity=100_000.0)
    price = float(prices.iloc[-1])
    target_units = int(weight * 100_000.0 / price)
    print(f"\n[live-paper] decision: raw={raw:+.0f} weight={weight:+.3f} "
          f"-> target {target_units} {SYMBOL} @ ~{price:.2f}")

    venue = IBKRVenue()  # host/port/client id from .env
    try:
        held = venue.positions().get(SYMBOL, 0.0)
        delta = target_units - held
        if delta == 0:
            print("  already at target — no order.")
            return
        fill = venue.execute(Order(INSTRUMENT, delta), market_price=price)
        print(f"  FILLED {fill.units:+.0f} {SYMBOL} @ {fill.price:.2f} "
              f"(commission ${fill.cost:.2f}) — through the same venue seam.")
    finally:
        venue.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T1 thin thread")
    parser.add_argument("--live", action="store_true",
                        help="route today's decision to IBKR paper (gateway required)")
    args = parser.parse_args()

    prices = load_prices()
    backtest(prices)
    if args.live:
        live_paper(prices)
    else:
        print("\nnext: start IB Gateway (paper, port 7497) and run with --live")
    sys.exit(0)
