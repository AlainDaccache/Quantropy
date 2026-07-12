"""M5 tests: covariance (Monte Carlo ground truth), optimizers (hand-computed),
VaR/ES + backtests (catch what they should catch), factor risk model (exact
decomposition), attribution (identities)."""

import numpy as np
import pandas as pd
import pytest

from quantropy.evaluation import brinson, factor_attribution
from quantropy.portfolio import (
    ewma_covariance,
    hrp,
    ledoit_wolf,
    min_variance,
    risk_contributions,
    risk_parity,
    sample_covariance,
    tangency,
)
from quantropy.risk import (
    FactorRiskModel,
    christoffersen_test,
    expected_shortfall,
    kupiec_test,
    value_at_risk,
)


def frame(data, cols=None):
    idx = pd.bdate_range("2018-01-01", periods=len(data))
    return pd.DataFrame(data, index=idx, columns=cols)


class TestCovariance:
    def test_ledoit_wolf_intensity_and_shape(self):
        rng = np.random.default_rng(0)
        r = frame(rng.normal(0, 0.01, (300, 10)))
        lw = ledoit_wolf(r)
        assert 0.0 <= lw.attrs["shrinkage_intensity"] <= 1.0
        assert np.allclose(lw, lw.T)
        assert np.linalg.eigvalsh(lw.to_numpy()).min() > -1e-12  # PSD

    def test_invertible_when_assets_exceed_observations(self):
        """N=30 assets, T=20 obs: the sample covariance is singular; LW must not be."""
        rng = np.random.default_rng(1)
        r = frame(rng.normal(0, 0.01, (20, 30)))
        s = sample_covariance(r).to_numpy()
        assert np.linalg.matrix_rank(s) < 30  # singular, as expected
        lw = ledoit_wolf(r, target="identity").to_numpy()
        np.linalg.inv(lw)  # must not raise
        assert np.linalg.eigvalsh(lw).min() > 0

    def test_shrinkage_beats_sample_against_known_truth(self):
        """Monte Carlo with a KNOWN covariance: in the N~T regime, LW's Frobenius
        error must be below the sample estimator's — the reason it exists."""
        rng = np.random.default_rng(2)
        n, t = 25, 50
        vols = rng.uniform(0.008, 0.03, n)
        true = 0.3 * np.outer(vols, vols)
        np.fill_diagonal(true, vols**2)
        err_s, err_lw = [], []
        for _ in range(20):
            x = rng.multivariate_normal(np.zeros(n), true, size=t)
            r = frame(x)
            err_s.append(np.linalg.norm(sample_covariance(r).to_numpy() - true))
            err_lw.append(np.linalg.norm(ledoit_wolf(r).to_numpy() - true))
        assert np.mean(err_lw) < np.mean(err_s)

    def test_ewma_tracks_the_recent_regime(self):
        rng = np.random.default_rng(3)
        calm = rng.normal(0, 0.005, (400, 2))
        wild = rng.normal(0, 0.03, (100, 2))
        r = frame(np.vstack([calm, wild]))
        ew_var = ewma_covariance(r, halflife=30).iloc[0, 0]
        samp_var = sample_covariance(r).iloc[0, 0]
        assert ew_var > samp_var * 2  # EWMA lives in the present


class TestOptimizers:
    def test_min_variance_two_asset_hand_computed(self):
        """Uncorrelated, variances 0.04 and 0.01 -> w = (0.2, 0.8)."""
        cov = pd.DataFrame([[0.04, 0.0], [0.0, 0.01]], index=list("ab"), columns=list("ab"))
        w = min_variance(cov)
        assert w["a"] == pytest.approx(0.2)
        assert w["b"] == pytest.approx(0.8)

    def test_tangency_proportional_to_mu_when_cov_is_identity(self):
        cov = pd.DataFrame(np.eye(2) * 0.01, index=list("ab"), columns=list("ab"))
        w = tangency(cov, pd.Series({"a": 0.10, "b": 0.05}))
        assert w["a"] == pytest.approx(2 / 3)
        assert w["b"] == pytest.approx(1 / 3)

    def test_risk_parity_equalizes_contributions(self):
        rng = np.random.default_rng(4)
        a = rng.normal(0, 1, (300, 4)) @ np.diag([0.01, 0.02, 0.015, 0.03])
        cov = sample_covariance(frame(a))
        w = risk_parity(cov)
        rc = risk_contributions(w, cov)
        assert np.allclose(rc, 0.25, atol=1e-6)
        assert (w > 0).all() and w.sum() == pytest.approx(1.0)

    def test_risk_parity_uncorrelated_is_inverse_vol(self):
        """Uncorrelated two-asset ERC: w_i proportional to 1/sigma_i -> (1/3, 2/3)."""
        cov = pd.DataFrame([[0.04, 0.0], [0.0, 0.01]], index=list("ab"), columns=list("ab"))
        w = risk_parity(cov)
        assert w["a"] == pytest.approx(1 / 3, abs=1e-6)
        assert w["b"] == pytest.approx(2 / 3, abs=1e-6)

    def test_hrp_allocates_across_correlation_blocks(self):
        """Two internal-0.9-correlation blocks, uncorrelated across: HRP must put
        meaningful weight in BOTH blocks (naive inverse-variance inside one)."""
        rng = np.random.default_rng(5)
        f1, f2 = rng.normal(0, 0.01, (500, 1)), rng.normal(0, 0.01, (500, 1))
        block1 = f1 + rng.normal(0, 0.003, (500, 3))
        block2 = f2 + rng.normal(0, 0.003, (500, 3))
        cov = sample_covariance(frame(np.hstack([block1, block2])))
        w = hrp(cov)
        assert w.sum() == pytest.approx(1.0)
        assert (w > 0).all()
        assert 0.3 < w.iloc[:3].sum() < 0.7  # both blocks meaningfully held

    def test_hrp_identity_cov_is_equal_weight(self):
        cov = pd.DataFrame(np.eye(4) * 0.01, index=list("abcd"), columns=list("abcd"))
        assert np.allclose(hrp(cov), 0.25)


class TestVaR:
    def test_parametric_normal_hand_computed(self):
        rng = np.random.default_rng(6)
        r = pd.Series(rng.normal(0, 0.01, 5000))
        r = (r - r.mean()) / r.std(ddof=1) * 0.01  # exact mean 0, sd 0.01
        assert value_at_risk(r, 0.99, "parametric") == pytest.approx(0.02326, abs=1e-4)

    def test_es_exceeds_var(self):
        rng = np.random.default_rng(7)
        r = pd.Series(rng.standard_t(4, 3000) * 0.01)  # fat tails
        assert expected_shortfall(r, 0.99) > value_at_risk(r, 0.99)

    def test_kupiec_accepts_correct_model_rejects_optimistic_one(self):
        rng = np.random.default_rng(8)
        r = pd.Series(rng.normal(0, 0.01, 2000))
        correct = pd.Series(0.01 * 2.326, index=r.index)  # true 99% VaR
        optimistic = correct / 2.0  # claims half the risk
        assert kupiec_test(r, correct, 0.99)["p_value"] > 0.05
        assert kupiec_test(r, optimistic, 0.99)["p_value"] < 0.001

    def test_christoffersen_catches_clustered_breaches(self):
        """Calm regime + one violent stretch, CONSTANT VaR forecast: breaches all
        cluster in the stretch — independence must reject even if counts look ok."""
        rng = np.random.default_rng(9)
        calm = rng.normal(0, 0.004, 1900)
        crisis = rng.normal(0, 0.04, 100)
        r = pd.Series(np.concatenate([calm[:1000], crisis, calm[1000:]]))
        var_const = pd.Series(np.quantile(-r, 0.99), index=r.index)
        out = christoffersen_test(r, var_const, 0.99)
        assert out["p_value"] < 0.01
        assert out["transition_11"] > 0


class TestFactorRiskModel:
    def test_recovers_planted_structure_and_decomposes_exactly(self):
        rng = np.random.default_rng(10)
        t = 1000
        f = frame(rng.normal(0, [0.01, 0.006], (t, 2)), cols=["MKT", "RATE"])
        true_b = np.array([[1.0, 0.2], [0.8, -0.5], [1.2, 0.1], [0.5, 0.9]])
        idio = rng.normal(0, 0.005, (t, 4))
        assets = frame(f.to_numpy() @ true_b.T + idio, cols=list("wxyz"))
        model = FactorRiskModel(assets, f)
        assert np.allclose(model.betas.to_numpy(), true_b, atol=0.06)

        w = pd.Series(0.25, index=list("wxyz"))
        d = model.portfolio_variance(w)
        assert d["total"] == pytest.approx(d["systematic"] + d["specific"], rel=1e-12)
        # in-model total ~ realized portfolio variance
        realized = (assets @ w).var(ddof=1)
        assert d["total"] == pytest.approx(realized, rel=0.1)


class TestAttribution:
    def test_brinson_hand_computed_and_identity(self):
        """Two sectors. Benchmark 50/50 earning 10%/2% (Rb=6%). Portfolio 70/30
        earning 12%/2%: allocation=(0.2)(0.10-0.06)+(-0.2)(0.02-0.06)=0.016;
        selection=0.5(0.02)+0=0.01; interaction=0.2*0.02=0.004; active=3.0%."""
        out = brinson(
            portfolio_weights=pd.Series({"tech": 0.7, "util": 0.3}),
            benchmark_weights=pd.Series({"tech": 0.5, "util": 0.5}),
            portfolio_returns=pd.Series({"tech": 0.12, "util": 0.02}),
            benchmark_returns=pd.Series({"tech": 0.10, "util": 0.02}),
        )
        assert out["allocation"].sum() == pytest.approx(0.016)
        assert out["selection"].sum() == pytest.approx(0.010)
        assert out["interaction"].sum() == pytest.approx(0.004)
        assert out.attrs["active_return"] == pytest.approx(out.to_numpy().sum())

    def test_factor_attribution_sums_to_mean_return_exactly(self):
        rng = np.random.default_rng(11)
        f = frame(rng.normal(0.0004, 0.01, (800, 2)), cols=["MKT", "HML"])
        y = 0.9 * f["MKT"] + 0.3 * f["HML"] + rng.normal(0.0001, 0.004, 800)
        contrib = factor_attribution(y, f)
        assert contrib["total"] == pytest.approx(y.mean(), rel=1e-9)
        assert contrib["MKT"] == pytest.approx(0.9 * f["MKT"].mean(), rel=0.2)
