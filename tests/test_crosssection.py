"""Tests for the cross-sectional toolkit — two validation layers:

1. Synthetic ground truth: the estimators must RECOVER premia we planted.
2. Real Ken French data (committed fixtures, 1963-07..2024-12): reproduce the
   published stylized facts (equity premium magnitude, GRS rejecting FF3 on the
   25 size/B-M portfolios).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quantropy.research import (
    fama_macbeth,
    grs_test,
    portfolio_sorts,
    two_pass_fama_macbeth,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def ff3():
    f = pd.read_csv(FIXTURES / "ff3_monthly.csv", index_col=0, parse_dates=True)
    return f


@pytest.fixture(scope="module")
def p25(ff3):
    p = pd.read_csv(FIXTURES / "p25_monthly.csv", index_col=0, parse_dates=True)
    return p.sub(ff3["RF"], axis=0)  # excess returns


class TestPortfolioSorts:
    def test_recovers_planted_cross_sectional_spread(self):
        """20 assets; asset i earns mean i*10bp/period. Sorting on a constant
        'quality' characteristic must earn Q5-Q1 ~= the planted mean difference."""
        rng = np.random.default_rng(0)
        n, t = 20, 2000
        means = np.arange(n) * 0.001
        rets = pd.DataFrame(rng.normal(means, 0.01, (t, n)),
                            columns=[f"a{i}" for i in range(n)])
        char = pd.DataFrame(np.tile(means, (t, 1)), columns=rets.columns)
        out = portfolio_sorts(rets, char, n_quantiles=5)
        planted = means[16:].mean() - means[:4].mean()  # top vs bottom quartile of 20
        assert out["spread"].mean() == pytest.approx(planted, abs=0.0015)

    def test_characteristic_is_lagged_a_contemporaneous_char_earns_nothing(self):
        """The API lags internally: sorting on THIS period's (iid) return gives no
        spread on NEXT period's return. If this test fails, the sort is peeking."""
        rng = np.random.default_rng(1)
        rets = pd.DataFrame(rng.normal(0, 0.01, (3000, 20)))
        rets.columns = [f"a{i}" for i in range(20)]
        out = portfolio_sorts(rets, characteristic=rets, n_quantiles=5)
        t_stat = out["spread"].mean() / (out["spread"].std() / np.sqrt(out["spread"].count()))
        assert abs(t_stat) < 3.0  # no spread beyond noise

    def test_value_weighting_uses_weights(self):
        rng = np.random.default_rng(2)
        rets = pd.DataFrame(rng.normal(0, 0.01, (300, 10)))
        rets.columns = [f"a{i}" for i in range(10)]
        char = pd.DataFrame(np.tile(np.arange(10), (300, 1)), columns=rets.columns)
        w = pd.DataFrame(1.0, index=rets.index, columns=rets.columns)
        ew = portfolio_sorts(rets, char, 5)
        vw = portfolio_sorts(rets, char, 5, weights=w)  # equal weights -> identical
        pd.testing.assert_frame_equal(ew.dropna(), vw.dropna())

    def test_mismatched_columns_rejected(self):
        a = pd.DataFrame(np.zeros((5, 3)), columns=list("abc"))
        b = pd.DataFrame(np.zeros((5, 3)), columns=list("abd"))
        with pytest.raises(ValueError):
            portfolio_sorts(a, b)


class TestFamaMacBeth:
    def test_recovers_planted_premium(self):
        """r[t,i] = 0.005 * x[t,i] + noise -> lambda_hat ~= 0.005, t-stat large."""
        rng = np.random.default_rng(3)
        t, n = 1500, 50
        x = pd.DataFrame(rng.normal(0, 1, (t, n)))
        rets = 0.005 * x + pd.DataFrame(rng.normal(0, 0.01, (t, n)))
        fm = fama_macbeth(rets, {"x": x})
        assert fm.premia["x"] == pytest.approx(0.005, abs=0.0005)
        assert fm.t_stats["x"] > 10
        assert fm.premia["const"] == pytest.approx(0.0, abs=0.0005)

    def test_no_premium_means_no_t_stat(self):
        rng = np.random.default_rng(4)
        t, n = 1000, 40
        x = pd.DataFrame(rng.normal(0, 1, (t, n)))
        rets = pd.DataFrame(rng.normal(0, 0.01, (t, n)))
        fm = fama_macbeth(rets, {"x": x})
        assert abs(fm.t_stats["x"]) < 3.0

    def test_two_pass_recovers_factor_premium_and_shanken_deflates(self):
        """Simulate a one-factor economy with a known premium; the two-pass must
        recover it, and the Shanken t must be smaller than the naive FM t."""
        rng = np.random.default_rng(5)
        t, n = 1200, 30
        premium = 0.006
        f = pd.DataFrame({"MKT": rng.normal(premium, 0.04, t)})
        betas = rng.uniform(0.5, 1.5, n)
        rets = pd.DataFrame(
            betas * f["MKT"].to_numpy()[:, None] + rng.normal(0, 0.02, (t, n)),
            columns=[f"a{i}" for i in range(n)],
        )
        res = two_pass_fama_macbeth(rets, f)
        assert res.premia["MKT"] == pytest.approx(premium, rel=0.35)
        assert 0 < res.shanken_t_stats["MKT"] < res.t_stats["MKT"]


class TestGRS:
    def test_zero_alpha_economy_is_not_rejected(self):
        rng = np.random.default_rng(6)
        t, n = 800, 10
        f = pd.DataFrame({"MKT": rng.normal(0.005, 0.04, t)})
        betas = rng.uniform(0.5, 1.5, n)
        rets = pd.DataFrame(betas * f["MKT"].to_numpy()[:, None] + rng.normal(0, 0.02, (t, n)))
        rets.columns = [f"a{i}" for i in range(n)]
        res = grs_test(rets, f)
        assert res.p_value > 0.05

    def test_planted_alpha_is_rejected(self):
        rng = np.random.default_rng(7)
        t, n = 800, 10
        f = pd.DataFrame({"MKT": rng.normal(0.005, 0.04, t)})
        betas = rng.uniform(0.5, 1.5, n)
        rets = pd.DataFrame(betas * f["MKT"].to_numpy()[:, None] + rng.normal(0, 0.02, (t, n)))
        rets.columns = [f"a{i}" for i in range(n)]
        rets.iloc[:, :3] += 0.004  # 40bp/mo alpha on three assets
        res = grs_test(rets, f)
        assert res.p_value < 0.01
        assert res.alpha_t_stats.iloc[:3].min() > 2.0

    def test_needs_enough_observations(self):
        f = pd.DataFrame({"MKT": np.zeros(20)})
        rets = pd.DataFrame(np.zeros((20, 25)))
        with pytest.raises(ValueError, match="T > N"):
            grs_test(rets, f)


class TestAgainstRealFrenchData:
    """The fixtures are REAL library data (1963-07..2024-12). These pin the
    stylized facts every empirical-asset-pricing course reproduces."""

    def test_equity_premium_magnitude_and_significance(self, ff3):
        mkt = ff3["Mkt-RF"]
        assert mkt.mean() * 100 == pytest.approx(0.5867, abs=0.01)  # %/month, pinned
        t = mkt.mean() / (mkt.std() / np.sqrt(len(mkt)))
        assert t > 3.0  # the premium is real (t ~= 3.9 over this sample)

    def test_value_premium_within_small_caps(self, ff3, p25):
        """SMALL HiBM minus SMALL LoBM — the classic value spread — positive and
        economically large over the long sample."""
        spread = p25["SMALL HiBM"] - p25["SMALL LoBM"]
        assert spread.mean() * 100 > 0.4  # > 40bp/month

    def test_grs_rejects_ff3_on_the_25_portfolios(self, ff3, p25):
        """The famous result (GRS 1989; Fama-French 1993 table 9c territory):
        FF3 prices the 25 size/B-M portfolios imperfectly — the joint-alpha test
        rejects decisively over the long sample."""
        res = grs_test(p25, ff3[["Mkt-RF", "SMB", "HML"]])
        assert res.p_value < 0.01
        assert res.statistic > 2.0

    def test_two_pass_market_premium_on_25_portfolios(self, ff3, p25):
        """Two-pass FM of the 25 portfolios on FF3: premia estimates exist, and
        the flat-SML stylized fact shows up (market premium estimate below the
        time-series mean)."""
        res = two_pass_fama_macbeth(p25, ff3[["Mkt-RF", "SMB", "HML"]])
        assert np.isfinite(res.premia[["Mkt-RF", "SMB", "HML"]]).all()
        assert res.premia["Mkt-RF"] < ff3["Mkt-RF"].mean()  # Black-Jensen-Scholes lives
