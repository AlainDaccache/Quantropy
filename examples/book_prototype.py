"""The flagship book, in miniature — a diversified multi-sleeve ETF prototype.

The dry run of MASTER_SPEC M2's futures book, on liquid ETFs (SPY equities, TLT
duration, GLD gold, EFA international): TSMOM sleeves, vol-targeted per sleeve,
combined risk-weighted, vol-targeted again at the book level — evaluated the only
way this project evaluates anything:

    hypothesis registered BEFORE the study → every configuration logged as a
    trial → the book uses the PRE-REGISTERED config (never the best-looking one)
    → deflated Sharpe against the ledger's cumulative trials → PBO across the
    config grid → pre-committed acceptance gates.

Run:  python examples/book_prototype.py     (fetches once to a local snapshot)
Numbers printed are [backtest], raw where marked raw, deflated where marked
deflated. This is a toy universe — the point is the WORKFLOW.
"""

from __future__ import annotations

import os

import pandas as pd

from quantropy.backtest import BacktestConfig, RiskLimits, SimulatedVenue, run_backtest
from quantropy.data import AssetClass, Instrument, SnapshotStore
from quantropy.evaluation import (
    AcceptanceGates,
    deflated_sharpe,
    pbo,
    sharpe_confidence_interval,
    summary,
)
from quantropy.evaluation.metrics import max_drawdown
from quantropy.portfolio import VolatilityTarget, combine_sleeves
from quantropy.research import TimeSeriesMomentum, TrialsLedger

SYMBOLS = ["SPY", "TLT", "GLD", "EFA"]
SNAPSHOT_ID = "book-proto-etf-daily"
STORE_ROOT = os.path.join(os.path.dirname(__file__), "..", "data")
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "research_log", "book_prototype.jsonl")

# ---- pre-registered choices (decided before looking at results) ---------------
LOOKBACK_GRID = (126, 252)  # every cell is logged as a trial
PREREGISTERED_LOOKBACK = 252  # the book uses THIS one, win or lose
SLEEVE_VOL, BOOK_VOL = 0.10, 0.10
GATES = AcceptanceGates(min_deflated_sharpe=0.75, max_drawdown=0.30, min_bars=2500,
                        max_pbo=0.50)


def load_panel() -> pd.DataFrame:
    store = SnapshotStore(STORE_ROOT)
    if SNAPSHOT_ID not in store.snapshots():
        print(f"fetching {SYMBOLS} -> snapshot {SNAPSHOT_ID!r} (one-time) ...")
        from quantropy.data.providers import use_system_trust
        from quantropy.data.providers.yahoo import fetch_daily

        use_system_trust()
        store.write(SNAPSHOT_ID, fetch_daily(SYMBOLS), note="book prototype (yahoo)")
    closes = {s: SnapshotStore(STORE_ROOT).read(SNAPSHOT_ID, s)["AdjClose"] for s in SYMBOLS}
    panel = pd.DataFrame(closes).dropna()  # common history only
    return panel.loc["2005-01-01":]


def sleeve_returns(prices: pd.Series, lookback: int) -> pd.Series:
    """One TSMOM sleeve through the real engine (costs, limits, vol targeting)."""
    result = run_backtest(
        prices,
        TimeSeriesMomentum(lookback=lookback),
        VolatilityTarget(target_vol=SLEEVE_VOL, lookback=63, max_leverage=2.0),
        Instrument(str(prices.name), AssetClass.ETF),
        limits=RiskLimits(max_leverage=2.0, max_drawdown=0.99),  # book-level DD guard below
        venue=SimulatedVenue(slippage_bps=1.0, cost_bps=1.0),
        config=BacktestConfig(initial_cash=100_000.0, snapshot_id=SNAPSHOT_ID),
    )
    return result.equity.pct_change().fillna(0.0).rename(f"{prices.name}_{lookback}")


def main() -> None:
    panel = load_panel()
    print(f"panel: {panel.shape[0]} bars, {panel.index[0].date()} -> {panel.index[-1].date()}")

    ledger = TrialsLedger(LEDGER_PATH)
    if not ledger.hypotheses():
        hyp = ledger.register_hypothesis(
            "etf-tsmom-book",
            "Time-series momentum harvests slow risk transfer across asset classes; "
            "a diversified, vol-targeted combination should carry a higher risk-"
            "adjusted return than any sleeve (Moskowitz-Ooi-Pedersen 2012; "
            "REFERENCES §2).",
        )
    else:
        hyp = ledger.hypotheses()[0]["id"]

    # ---- run the FULL pre-registered grid; log every cell as a trial ----------
    grid: dict[str, pd.Series] = {}
    for lb in LOOKBACK_GRID:
        for sym in SYMBOLS:
            rets = sleeve_returns(panel[sym], lb)
            grid[rets.name] = rets
            if ledger.n_trials() < len(LOOKBACK_GRID) * len(SYMBOLS):
                sd = rets.std(ddof=1)
                ledger.log_trial(
                    hyp,
                    sharpe_per_period=float(rets.mean() / sd) if sd > 0 else 0.0,
                    n_obs=int(len(rets)),
                    params={"symbol": sym, "lookback": lb, "sleeve_vol": SLEEVE_VOL},
                )
    grid_frame = pd.DataFrame(grid).dropna()

    # ---- the book: PRE-REGISTERED config only ---------------------------------
    sleeves = grid_frame[[f"{s}_{PREREGISTERED_LOOKBACK}" for s in SYMBOLS]]
    book = combine_sleeves(sleeves, target_vol=BOOK_VOL, lookback=63)["book"]
    equity = 100_000.0 * (1.0 + book).cumprod()

    stats = summary(equity)
    dsr = deflated_sharpe(book, n_trials=ledger.n_trials(),
                          var_trial_sr=ledger.trial_sharpe_variance())
    ci_lo, ci_hi = sharpe_confidence_interval(book, seed=42)
    pbo_val = pbo(grid_frame, n_blocks=8)
    gates = GATES.evaluate(deflated_sharpe=dsr, max_dd=max_drawdown(equity),
                           n_bars=len(equity), pbo_value=pbo_val)

    print(f"\n[backtest] {len(SYMBOLS)}-sleeve TSMOM({PREREGISTERED_LOOKBACK}) book, "
          f"vol-target {BOOK_VOL:.0%}, costs+slippage+financing on")
    print(f"  CAGR={stats['cagr']:.2%}  vol={stats['ann_vol']:.2%}  "
          f"sharpe_raw={stats['sharpe_raw']:.2f}  maxDD={stats['max_drawdown']:.2%}")
    print(f"  sharpe 90% CI (block bootstrap): [{ci_lo:.2f}, {ci_hi:.2f}]")
    print(f"  deflated Sharpe (n_trials={ledger.n_trials()}, cumulative): {dsr:.3f}")
    print(f"  PBO across the {grid_frame.shape[1]}-config grid: {pbo_val:.2f}")
    print(f"  gates: {'PASS' if gates.passed else 'FAIL'}"
          + (f" — {'; '.join(gates.reasons)}" if gates.reasons else ""))
    print("\n  ledger:", os.path.relpath(LEDGER_PATH), "(append-only, committed)")
    print("  every number above is [backtest]; the paper track record starts at T1-live.")


if __name__ == "__main__":
    main()
