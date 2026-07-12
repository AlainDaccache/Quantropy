"""Tests: the trials ledger (governance semantics) and the sleeve combiner."""

import numpy as np
import pandas as pd
import pytest

from quantropy.portfolio import combine_sleeves
from quantropy.research import TrialsLedger


class TestTrialsLedger:
    def test_register_then_log_then_count(self, tmp_path):
        ledger = TrialsLedger(tmp_path / "ledger.jsonl")
        h = ledger.register_hypothesis("tsmom-etf", "risk transfer from hedgers")
        ledger.log_trial(h, sharpe_per_period=0.03, n_obs=2500, params={"lb": 252})
        ledger.log_trial(h, sharpe_per_period=0.05, n_obs=2500, params={"lb": 126})
        assert ledger.n_trials() == 2
        assert len(ledger.trials(h)) == 2

    def test_rationale_is_mandatory(self, tmp_path):
        ledger = TrialsLedger(tmp_path / "l.jsonl")
        with pytest.raises(ValueError, match="rationale"):
            ledger.register_hypothesis("no-reason", "")

    def test_cannot_log_against_unregistered_hypothesis(self, tmp_path):
        ledger = TrialsLedger(tmp_path / "l.jsonl")
        with pytest.raises(KeyError, match="register before testing"):
            ledger.log_trial("H999", 0.05, 1000)

    def test_variance_feeds_deflation(self, tmp_path):
        ledger = TrialsLedger(tmp_path / "l.jsonl")
        h = ledger.register_hypothesis("x", "y")
        assert ledger.trial_sharpe_variance() == 0.0  # nothing yet
        for sr in (0.01, 0.03, 0.05):
            ledger.log_trial(h, sr, 1000)
        assert ledger.trial_sharpe_variance() == pytest.approx(np.var([0.01, 0.03, 0.05], ddof=1))

    def test_ledger_persists_across_instances(self, tmp_path):
        path = tmp_path / "l.jsonl"
        h = TrialsLedger(path).register_hypothesis("a", "b")
        TrialsLedger(path).log_trial(h, 0.02, 500)
        assert TrialsLedger(path).n_trials() == 1  # append-only file IS the record


def sleeve_frame(n=1000, seed=0, vols=(0.01, 0.02)):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-01", periods=n)
    data = {f"s{i}": rng.normal(0.0002, v, n) for i, v in enumerate(vols)}
    return pd.DataFrame(data, index=idx)


class TestCombineSleeves:
    def test_inverse_vol_weights_favor_the_quiet_sleeve(self):
        out = combine_sleeves(sleeve_frame(vols=(0.01, 0.02)), target_vol=0.10)
        w = out[["s0_w", "s1_w"]].dropna()
        # 2x the vol -> ~half the weight: s0 should sit near 2/3, s1 near 1/3
        assert w["s0_w"].mean() == pytest.approx(2 / 3, abs=0.05)
        assert w["s1_w"].mean() == pytest.approx(1 / 3, abs=0.05)

    def test_weights_sum_to_one_when_live(self):
        out = combine_sleeves(sleeve_frame(), target_vol=0.10)
        sums = out[["s0_w", "s1_w"]].dropna().sum(axis=1)
        assert np.allclose(sums, 1.0)

    def test_diversification_beats_single_sleeve(self):
        """Two independent sleeves, equal vol: the risk-weighted mix must run at
        materially lower vol than either sleeve alone (~1/sqrt(2))."""
        frame = sleeve_frame(n=2000, vols=(0.01, 0.01), seed=3)
        out = combine_sleeves(frame, target_vol=0.10, max_leverage=1.0)  # cap leverage off
        mix = (out[["s0_w", "s1_w"]].to_numpy() * frame.to_numpy()).sum(axis=1)
        mix = pd.Series(mix, index=frame.index).dropna()
        ratio = mix.std() / frame["s0"].std()
        assert 0.6 < ratio < 0.8  # theory: 1/sqrt(2) ~= 0.707

    def test_book_realizes_near_target_vol(self):
        out = combine_sleeves(sleeve_frame(n=3000, seed=5), target_vol=0.10)
        realized = out["book"].iloc[200:].std(ddof=1) * np.sqrt(252)
        assert realized == pytest.approx(0.10, rel=0.15)

    def test_no_exposure_before_history_exists(self):
        out = combine_sleeves(sleeve_frame(n=300), target_vol=0.10, lookback=63)
        assert (out["book"].iloc[:63] == 0).all()  # can't measure risk -> no risk

    def test_causality_leverage_uses_only_past(self):
        """Changing the FINAL bar's returns must not change any prior leverage —
        the combiner obeys the same prefix-invariance law as the engine."""
        frame = sleeve_frame(n=500, seed=6)
        bumped = frame.copy()
        bumped.iloc[-1] = 0.5  # absurd final bar
        a = combine_sleeves(frame, target_vol=0.10)
        b = combine_sleeves(bumped, target_vol=0.10)
        pd.testing.assert_frame_equal(a.iloc[:-1], b.iloc[:-1])

    def test_bad_params_rejected(self):
        with pytest.raises(ValueError):
            combine_sleeves(sleeve_frame(), target_vol=-0.1)
