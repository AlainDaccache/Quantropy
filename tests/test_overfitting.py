"""Tests: PBO/CSCV, MinBTL (paper reference), acceptance gates, walk-forward harness."""

import numpy as np
import pandas as pd
import pytest

from quantropy.backtest.walkforward import run_walk_forward
from quantropy.data.model import AssetClass, Instrument
from quantropy.evaluation import AcceptanceGates, min_backtest_length, pbo


def strategies(t=1200, n=30, true_alpha_col=None, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 0.01, (t, n))
    if true_alpha_col is not None:
        r[:, true_alpha_col] += 0.0015  # a genuinely good config
    return pd.DataFrame(r, columns=[f"cfg{i}" for i in range(n)])


class TestPBO:
    def test_pure_noise_pbo_averages_to_half(self):
        """30 zero-alpha configs: IS selection can't generalize — E[PBO] = 0.5.
        A SINGLE dataset's PBO is itself noisy (CSCV combos share data), so the
        test averages over seeds — and that variance is itself a lesson."""
        vals = [pbo(strategies(seed=s), n_blocks=8) for s in range(10)]
        assert np.mean(vals) == pytest.approx(0.5, abs=0.12)

    def test_true_skill_pbo_low(self):
        """A config with real alpha: IS selection holds OOS — PBO near zero."""
        vals = [
            pbo(strategies(true_alpha_col=7, seed=100 + s), n_blocks=8) for s in range(5)
        ]
        assert np.mean(vals) < 0.15

    def test_input_validation(self):
        with pytest.raises(ValueError, match="even"):
            pbo(strategies(), n_blocks=7)
        with pytest.raises(ValueError, match="two strategy"):
            pbo(strategies().iloc[:, :1])
        with pytest.raises(ValueError, match="too short"):
            pbo(strategies(t=50), n_blocks=10)


class TestMinBTL:
    def test_paper_reference_45_trials_needs_5_years(self):
        """Bailey et al. (2014): ~45 trials at target SR=1 demand ~5 years."""
        assert min_backtest_length(45, 1.0) == pytest.approx(5.0, abs=0.35)

    def test_more_trials_demand_more_data_and_higher_sr_less(self):
        assert min_backtest_length(200, 1.0) > min_backtest_length(20, 1.0)
        assert min_backtest_length(45, 2.0) == pytest.approx(
            min_backtest_length(45, 1.0) / 4.0
        )

    def test_invalid_inputs(self):
        with pytest.raises(ValueError):
            min_backtest_length(1, 1.0)
        with pytest.raises(ValueError):
            min_backtest_length(45, 0.0)


class TestAcceptanceGates:
    GATES = AcceptanceGates(min_deflated_sharpe=0.90, max_drawdown=0.35, min_bars=750)

    def test_pass_when_all_criteria_met(self):
        rep = self.GATES.evaluate(deflated_sharpe=0.95, max_dd=0.20, n_bars=1000,
                                  pbo_value=0.2, oos_positive_frac=0.7)
        assert rep.passed and rep.reasons == []

    def test_every_failure_is_named(self):
        rep = self.GATES.evaluate(deflated_sharpe=0.50, max_dd=0.50, n_bars=100,
                                  pbo_value=0.8, oos_positive_frac=0.2)
        assert not rep.passed
        assert len(rep.reasons) == 5  # every violated criterion, spelled out

    def test_nan_dsr_fails_not_passes(self):
        """A NaN statistic must fail the gate — unmeasurable is not acceptable."""
        rep = self.GATES.evaluate(deflated_sharpe=float("nan"), max_dd=0.1, n_bars=1000)
        assert not rep.passed

    def test_optional_criteria_skipped_when_absent(self):
        rep = self.GATES.evaluate(deflated_sharpe=0.95, max_dd=0.2, n_bars=1000)
        assert rep.passed  # pbo/oos not supplied -> not evaluated


class TestWalkForwardHarness:
    def test_folds_run_and_score_oos_only(self):
        rng = np.random.default_rng(3)
        idx = pd.bdate_range("2015-01-01", periods=1500)
        prices = pd.Series(100 * np.cumprod(1 + rng.normal(0.0004, 0.01, 1500)), index=idx)

        from quantropy.backtest import RiskLimits, SimulatedVenue
        from quantropy.portfolio import VolatilityTarget
        from quantropy.research import TimeSeriesMomentum

        report = run_walk_forward(
            prices,
            signal_factory=lambda train: TimeSeriesMomentum(lookback=126),
            sizer=VolatilityTarget(target_vol=0.10, lookback=63),
            instrument=Instrument("SPY", AssetClass.ETF),
            train_size=500,
            test_size=200,
            embargo=5,
            venue=SimulatedVenue(slippage_bps=1, cost_bps=1),
            limits_factory=lambda: RiskLimits(max_leverage=2.0, max_drawdown=0.99),
        )
        assert len(report.folds) >= 3
        for f in report.folds:
            assert f.test_start > prices.index[0]  # OOS windows only
        assert 0.0 <= report.oos_positive_frac <= 1.0

    def test_too_short_series_raises(self):
        prices = pd.Series(np.ones(100), index=pd.bdate_range("2020-01-01", periods=100))
        from quantropy.portfolio import VolatilityTarget
        from quantropy.research import TimeSeriesMomentum

        with pytest.raises(ValueError, match="no folds"):
            run_walk_forward(
                prices, lambda t: TimeSeriesMomentum(20), VolatilityTarget(),
                Instrument("X", AssetClass.ETF), train_size=500, test_size=200,
            )
