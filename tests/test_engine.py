"""Invariant tests for the event-driven engine — the T1 contract.

These are the tests that make a backtest *believable*: no-look-ahead (prefix
invariance + impulse timing), exact hand-computed accounting (equities AND
futures), cost monotonicity, adverse slippage, and enforced (latching) risk
limits.
"""

import numpy as np
import pandas as pd
import pytest

from quantropy.backtest import BacktestConfig, RiskLimits, SimulatedVenue, run_backtest
from quantropy.data.model import AssetClass, Instrument

SPY = Instrument("SPY", AssetClass.ETF)
MES = Instrument("MES", AssetClass.FUTURE, multiplier=5.0, tick_size=0.25)


def series(values, start="2024-01-01"):
    idx = pd.bdate_range(start, periods=len(values))
    return pd.Series([float(v) for v in values], index=idx)


class PassThroughSizer:
    def scale(self, raw, history):
        return raw


class ConstantSignal:
    def __init__(self, weight=1.0):
        self.weight = weight

    def target(self, history):
        return self.weight


class ImpulseSignal:
    """Fires +1 exactly on bar index `k` (0-based), else 0."""

    def __init__(self, k):
        self.k = k

    def target(self, history):
        return 1.0 if len(history) == self.k + 1 else 0.0


def frictionless():
    return SimulatedVenue(slippage_bps=0.0, cost_bps=0.0, commission=0.0)


def run(prices, signal, instrument=SPY, venue=None, limits=None, cash=100_000.0):
    return run_backtest(
        prices,
        signal,
        PassThroughSizer(),
        instrument,
        limits=limits or RiskLimits(max_leverage=2.0, max_drawdown=0.99),
        venue=venue or frictionless(),
        config=BacktestConfig(initial_cash=cash),
    )


class TestNoLookAhead:
    def test_prefix_invariance(self):
        """Altering FUTURE prices must not change PAST equity/decisions — the
        single most important property of any backtest engine."""
        base = series(100 + np.cumsum(np.sin(np.arange(40))))
        wild = base.copy()
        wild.iloc[30:] = [1000, 1, 500, 2, 800, 3, 900, 4, 700, 5]  # absurd future

        from quantropy.research import MovingAverageCross

        sig = MovingAverageCross(fast=3, slow=8)
        r_base = run(base, sig)
        r_wild = run(wild, sig)
        # everything strictly before the divergence point must be identical
        pd.testing.assert_frame_equal(r_base.frame.iloc[:30], r_wild.frame.iloc[:30])

    def test_impulse_fills_next_bar_and_only_then(self):
        prices = series([100] * 10)
        res = run(prices, ImpulseSignal(k=4))
        pos = res.frame["position_units"].to_numpy()
        assert (pos[:5] == 0).all()  # decision on bar 4 — no position through bar 4
        assert pos[5] != 0  # filled exactly on bar 5
        assert pos[6] == 0  # bar-5 decision (0) fills bar 6: flat again

    def test_final_bar_decision_never_fills(self):
        prices = series([100, 100, 100])
        res = run(prices, ImpulseSignal(k=2))  # fires on the last bar
        assert (res.frame["position_units"] == 0).all()  # nowhere left to fill


class TestAccountingReferences:
    def test_equity_accounting_by_hand(self):
        """SPY, all-in decided at bar0: units = E0/P0 = 1000, bought at P1=102.
        cash = 100000 - 1000*102 = -2000; equity@P2=101: -2000 + 1000*101 = 99000."""
        prices = series([100, 102, 101])
        res = run(prices, ConstantSignal(1.0))
        assert res.equity.iloc[0] == pytest.approx(100_000)
        assert res.equity.iloc[1] == pytest.approx(100_000 + 1000 * (102 - 102))  # bought AT 102
        assert res.equity.iloc[2] == pytest.approx(-2000 + 1000 * 101)

    def test_futures_daily_settlement_by_hand(self):
        """MES (x5), target 1.0 at bar0 with E0=100000, P0=100 -> 200 contracts.
        Filled bar1; settle bar2: 200 * (98-102) * 5 = -4000."""
        prices = series([100, 102, 98])
        res = run(prices, ConstantSignal(1.0), instrument=MES)
        assert res.frame["position_units"].iloc[1] == pytest.approx(200.0)
        assert res.equity.iloc[1] == pytest.approx(100_000)  # opened at 102, no cash outlay
        assert res.equity.iloc[2] == pytest.approx(100_000 + 200 * (98 - 102) * 5)

    def test_nan_prices_rejected(self):
        prices = series([100, np.nan, 101])
        with pytest.raises(ValueError, match="NaN"):
            run(prices, ConstantSignal(1.0))


class TestFrictions:
    def test_cost_monotonicity(self):
        """More costs can never help: equity(0bps) > equity(10bps) > equity(50bps)."""
        rng = np.random.default_rng(7)
        prices = series(100 * np.cumprod(1 + rng.normal(0, 0.01, 120)))
        from quantropy.research import MovingAverageCross

        sig = MovingAverageCross(fast=5, slow=20)  # trades several times
        finals = []
        for bps in (0.0, 10.0, 50.0):
            venue = SimulatedVenue(slippage_bps=0.0, cost_bps=bps, commission=0.0)
            finals.append(run(prices, sig, venue=venue).equity.iloc[-1])
        assert finals[0] > finals[1] > finals[2]

    def test_slippage_is_always_adverse(self):
        venue = SimulatedVenue(slippage_bps=10.0, cost_bps=0.0, commission=0.0)
        from quantropy.backtest import Order

        buy = venue.execute(Order(SPY, 100), market_price=100.0)
        sell = venue.execute(Order(SPY, -100), market_price=100.0)
        assert buy.price > 100.0 and sell.price < 100.0

    def test_costs_accumulate_in_result(self):
        venue = SimulatedVenue(slippage_bps=0.0, cost_bps=10.0, commission=1.0)
        prices = series([100] * 6)
        res = run(prices, ImpulseSignal(k=2), venue=venue)
        assert res.total_costs > 0


class TestRiskLimits:
    def test_leverage_clamp(self):
        limits = RiskLimits(max_leverage=1.5, max_drawdown=0.99)
        assert limits.apply(3.0, equity=100_000) == pytest.approx(1.5)
        assert limits.apply(-3.0, equity=100_000) == pytest.approx(-1.5)

    def test_drawdown_kill_switch_latches(self):
        limits = RiskLimits(max_leverage=2.0, max_drawdown=0.10)
        assert limits.apply(1.0, equity=100_000) == 1.0  # sets the peak
        assert limits.apply(1.0, equity=85_000) == 0.0  # 15% dd -> killed
        assert limits.killed
        assert limits.apply(1.0, equity=200_000) == 0.0  # recovery does NOT re-arm
        limits.reset()
        assert limits.apply(1.0, equity=200_000) == 1.0  # human reset does

    def test_engine_flattens_after_breach(self):
        """Long into a crash: the switch must latch and the book must go flat."""
        prices = series([100, 100, 100, 70, 65, 64, 63, 62])
        limits = RiskLimits(max_leverage=2.0, max_drawdown=0.20)
        res = run(prices, ConstantSignal(1.0), limits=limits)
        assert res.killed
        assert res.frame["position_units"].iloc[-1] == 0.0
        assert (res.frame["target_weight"].iloc[4:] == 0).all()


class TestVolTargeting:
    def test_weight_matches_target_over_realized(self):
        from quantropy.portfolio import VolatilityTarget

        # alternating +/-1% daily returns -> annualized vol ~ 0.01*sqrt(252)
        values = 100 * np.cumprod(1 + 0.01 * np.array([1, -1] * 50))
        history = series(values)
        sizer = VolatilityTarget(target_vol=0.10, lookback=63, max_leverage=2.0)
        vol = sizer.realized_vol(history)
        assert vol == pytest.approx(0.01 * np.sqrt(252), rel=0.02)
        assert sizer.scale(1.0, history) == pytest.approx(0.10 / vol)

    def test_leverage_cap_binds_in_quiet_markets(self):
        from quantropy.portfolio import VolatilityTarget

        values = 100 * np.cumprod(1 + 0.0001 * np.array([1, -1] * 50))  # ~0.16% vol
        sizer = VolatilityTarget(target_vol=0.10, lookback=63, max_leverage=2.0)
        assert sizer.scale(1.0, series(values)) == pytest.approx(2.0)  # capped, not 63x

    def test_no_history_means_no_position(self):
        from quantropy.portfolio import VolatilityTarget

        sizer = VolatilityTarget(target_vol=0.10, lookback=63)
        assert sizer.scale(1.0, series([100, 101, 102])) == 0.0


class TestSignals:
    def test_ma_cross_goes_long_in_uptrend_flat_in_downtrend(self):
        from quantropy.research import MovingAverageCross

        sig = MovingAverageCross(fast=2, slow=4)
        up = series([100, 101, 102, 103, 104, 105])
        down = series([105, 104, 103, 102, 101, 100])
        assert sig.target(up) == 1.0
        assert sig.target(down) == 0.0

    def test_insufficient_history_is_flat(self):
        from quantropy.research import MovingAverageCross

        assert MovingAverageCross(fast=2, slow=10).target(series([100, 101])) == 0.0
