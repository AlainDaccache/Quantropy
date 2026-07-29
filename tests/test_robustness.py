"""Tests for the honesty statistics (PSR/DSR/bootstrap/walk-forward).

Reference style: hand-derived values where the formula permits, plus the
behavioral properties that make the statistics meaningful (deflation hurts,
negative skew hurts, more trials raise the hurdle).
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from quantropy.evaluation import (
    deflated_sharpe,
    expected_max_sharpe,
    probabilistic_sharpe,
    sharpe_confidence_interval,
    walk_forward_splits,
)


def gaussian_returns(mean, std, n, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.Series(rng.normal(mean, std, n), index=idx)


class TestProbabilisticSharpe:
    def test_hand_derived_gaussian_case(self):
        """For exactly-normal returns with per-period SR=0.05, n=1000:
        z = 0.05*sqrt(999)/sqrt(1 + (3-1)/4*0.0025) ~= 1.5794 -> PSR ~= 0.9428.
        Built synthetically so sample moments match the assumption closely."""
        r = gaussian_returns(0.0005, 0.01, 1000, seed=42)
        r = (r - r.mean()) / r.std(ddof=1) * 0.01 + 0.0005  # pin SR to 0.05 exactly
        psr = probabilistic_sharpe(r, benchmark_sr=0.0)
        # exact z for the *sample's* skew/kurt; hand value for the normal case
        assert psr == pytest.approx(0.9428, abs=0.02)

    def test_zero_mean_is_a_coin_flip(self):
        r = gaussian_returns(0.0, 0.01, 2000, seed=1)
        r = r - r.mean()  # exactly zero sample mean -> SR = 0
        assert probabilistic_sharpe(r) == pytest.approx(0.5, abs=1e-6)

    def test_longer_samples_are_more_convincing(self):
        rng = np.random.default_rng(3)
        vals = rng.normal(0.0004, 0.01, 4000)
        short = pd.Series(vals[:500])
        long = pd.Series(vals)
        if short.mean() > 0 and long.mean() > 0:  # same draw, more evidence
            assert probabilistic_sharpe(long) > probabilistic_sharpe(short)

    def test_negative_skew_reduces_credibility(self):
        """Two series, same mean/std/SR — the negatively-skewed one must earn a
        lower PSR (its Sharpe is more fragile). This is the whole point of PSR."""
        rng = np.random.default_rng(7)
        sym = pd.Series(rng.normal(0, 1, 3000))
        skewed = -pd.Series(rng.lognormal(0, 0.7, 3000))  # heavy left tail
        # normalize both to identical mean/std -> identical SR
        sym = (sym - sym.mean()) / sym.std(ddof=1) * 0.01 + 0.0005
        skewed = (skewed - skewed.mean()) / skewed.std(ddof=1) * 0.01 + 0.0005
        assert stats.skew(skewed) < -0.5 < 0.5  # sanity: it is actually skewed
        assert probabilistic_sharpe(skewed) < probabilistic_sharpe(sym)


class TestDeflatedSharpe:
    def test_hurdle_grows_with_trials(self):
        v = 0.001
        hurdles = [expected_max_sharpe(n, v) for n in (2, 10, 100, 1000)]
        assert hurdles == sorted(hurdles) and hurdles[0] > 0

    def test_single_trial_means_no_deflation(self):
        assert expected_max_sharpe(1, 0.001) == 0.0
        r = gaussian_returns(0.0005, 0.01, 1000, seed=5)
        assert deflated_sharpe(r, n_trials=1, var_trial_sr=0.001) == pytest.approx(
            probabilistic_sharpe(r)
        )

    def test_deflation_only_hurts(self):
        r = gaussian_returns(0.0005, 0.01, 1000, seed=6)
        psr = probabilistic_sharpe(r)
        dsr = deflated_sharpe(r, n_trials=200, var_trial_sr=0.002)
        assert dsr < psr

    def test_a_lucky_best_of_many_fails_deflation(self):
        """The core scenario: pick the best of 200 zero-alpha strategies; PSR is
        fooled, DSR is not."""
        rng = np.random.default_rng(11)
        trials = [pd.Series(rng.normal(0, 0.01, 750)) for _ in range(200)]
        srs = [t.mean() / t.std(ddof=1) for t in trials]
        best = trials[int(np.argmax(srs))]
        psr = probabilistic_sharpe(best)
        dsr = deflated_sharpe(best, n_trials=200, var_trial_sr=float(np.var(srs, ddof=1)))
        assert psr > 0.95  # luck looks convincing...
        assert dsr < 0.65  # ...until you count the trials

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError):
            expected_max_sharpe(0, 0.001)
        with pytest.raises(ValueError):
            expected_max_sharpe(10, -1.0)


class TestBootstrapCI:
    def test_reproducible_and_contains_point_estimate(self):
        r = gaussian_returns(0.0004, 0.01, 1500, seed=8)
        lo1, hi1 = sharpe_confidence_interval(r, seed=123)
        lo2, hi2 = sharpe_confidence_interval(r, seed=123)
        assert (lo1, hi1) == (lo2, hi2)  # seeded determinism (P5)
        point = r.mean() / r.std(ddof=1) * np.sqrt(252)
        assert lo1 < point < hi1

    def test_interval_narrows_with_sample_size(self):
        rng = np.random.default_rng(9)
        vals = rng.normal(0.0004, 0.01, 6000)
        lo_s, hi_s = sharpe_confidence_interval(pd.Series(vals[:1000]), seed=1)
        lo_l, hi_l = sharpe_confidence_interval(pd.Series(vals), seed=1)
        assert (hi_l - lo_l) < (hi_s - lo_s)

    def test_too_short_series_rejected(self):
        with pytest.raises(ValueError):
            sharpe_confidence_interval(gaussian_returns(0, 0.01, 30), block=21)


class TestWalkForward:
    def test_windows_disjoint_embargoed_and_ordered(self):
        idx = pd.bdate_range("2020-01-01", periods=500)
        splits = walk_forward_splits(idx, train_size=200, test_size=50, embargo=5)
        assert len(splits) >= 4
        for s in splits:
            assert len(s.train) == 200 and len(s.test) == 50
            gap = idx.get_loc(s.test[0]) - idx.get_loc(s.train[-1]) - 1
            assert gap == 5  # embargo respected
            assert s.train[-1] < s.test[0]  # strictly forward in time
        # test sets never overlap
        all_test = [d for s in splits for d in s.test]
        assert len(all_test) == len(set(all_test))

    def test_degenerate_params_rejected(self):
        idx = pd.bdate_range("2020-01-01", periods=100)
        with pytest.raises(ValueError):
            walk_forward_splits(idx, train_size=1, test_size=10)
