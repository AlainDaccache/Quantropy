"""Fixed-income tests: hand-computed bond math, exact bootstrap round-trips, the
Fed's own NSS-vs-published-yields consistency, and Litterman-Scheinkman on real
curve history."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quantropy.pricing import (
    DiscountCurve,
    bond_price,
    bootstrap_par_curve,
    dv01,
    key_rate_durations,
    macaulay_duration,
    modified_duration,
    nss_yield,
    pca_level_slope_curvature,
)

FIXTURE = Path(__file__).parent / "fixtures" / "gsw_monthly.csv"


@pytest.fixture(scope="module")
def gsw():
    return pd.read_csv(FIXTURE, index_col=0, parse_dates=True)


def flat_curve(rate=0.04, n=30):
    return DiscountCurve(np.arange(1.0, n + 1.0), np.full(n, rate))


class TestBondMath:
    def test_price_by_hand(self):
        """2y 5% annual coupon at flat 4%: 5/1.04 + 105/1.04^2 = 101.8861 (per 100)."""
        p = bond_price(0.05, 2, flat_curve(0.04))
        assert p * 100 == pytest.approx(101.8861, abs=0.001)

    def test_par_bond_prices_at_par(self):
        assert bond_price(0.04, 10, flat_curve(0.04)) == pytest.approx(1.0, abs=1e-12)

    def test_zero_coupon_macaulay_equals_maturity(self):
        assert macaulay_duration(0.0, 7, 0.05) == pytest.approx(7.0)
        assert modified_duration(0.0, 7, 0.05) == pytest.approx(7.0 / 1.05)

    def test_coupon_bond_duration_by_hand(self):
        """2y 5% at 4%: weights from PVs 4.8077(t=1), 97.0784(t=2) ->
        D = (1*4.8077 + 2*97.0784)/101.8861 = 1.95281..."""
        d = macaulay_duration(0.05, 2, 0.04)
        assert d == pytest.approx((4.8077 + 2 * 97.0784) / 101.8861, abs=1e-4)

    def test_dv01_matches_modified_duration_at_flat_curve(self):
        """For a par bond on a flat curve, DV01 ~= P * D_mod * 1bp."""
        curve = flat_curve(0.04)
        approx = 1.0 * modified_duration(0.04, 10, 0.04) * 1e-4
        assert dv01(0.04, 10, curve) == pytest.approx(approx, rel=0.01)

    def test_no_silent_extrapolation(self):
        with pytest.raises(ValueError, match="extrapolation"):
            flat_curve(n=10).zero(15.0)


class TestBootstrap:
    def test_flat_par_curve_gives_flat_zeros(self):
        curve = bootstrap_par_curve({n: 0.04 for n in range(1, 11)})
        assert np.allclose(curve.zero_rates, 0.04, atol=1e-12)

    def test_roundtrip_recovers_zeros_exactly(self):
        """zeros -> par yields -> bootstrap -> the same zeros. The defining test."""
        true = DiscountCurve(np.arange(1.0, 11.0),
                             0.02 + 0.02 * (1 - np.exp(-np.arange(1, 11) / 4)))
        pars = {}
        for n in range(1, 11):
            annuity = sum(true.discount(t) for t in range(1, n + 1))
            pars[n] = (1.0 - true.discount(n)) / annuity  # par coupon identity
        rebuilt = bootstrap_par_curve(pars)
        assert np.allclose(rebuilt.zero_rates, true.zero_rates, atol=1e-12)

    def test_upward_par_curve_zeros_above_pars(self):
        """With an upward-sloping curve, zeros sit above par yields (coupon drag)."""
        pars = {n: 0.02 + 0.002 * n for n in range(1, 11)}
        curve = bootstrap_par_curve(pars)
        assert curve.zero_rates[-1] > pars[10]

    def test_gaps_rejected(self):
        with pytest.raises(ValueError, match="consecutive"):
            bootstrap_par_curve({1: 0.03, 3: 0.035})


class TestKeyRates:
    def test_krd_sums_to_parallel_dv01(self):
        curve = flat_curve(0.04)
        krd = key_rate_durations(0.04, 10, curve)
        total = dv01(0.04, 10, curve)
        assert krd.sum() == pytest.approx(total, rel=0.02)

    def test_exposure_concentrates_at_the_bond_maturity(self):
        krd = key_rate_durations(0.04, 10, flat_curve(0.04))
        assert krd["10y"] == krd.max()  # a 10y bond is mostly 10y risk
        assert krd["30y"] < krd["10y"] * 0.2


class TestNSSAgainstTheFed:
    def test_nss_limits(self):
        assert nss_yield(1e9, 4.0, -1.0, 2.0, 0.5, 1.4, 8.0) == pytest.approx(4.0, abs=1e-3)
        assert nss_yield(1e-9, 4.0, -1.0, 2.0, 0.5, 1.4, 8.0) == pytest.approx(3.0, abs=1e-3)

    def test_fed_parameters_reproduce_fed_yields(self, gsw):
        """The GSW file's own consistency: BETA/TAU columns must reproduce the
        published SVENY yields. Checked across dates and maturities to ~1bp —
        this validates our NSS implementation against the Fed's."""
        for date in ["1995-06-30", "2008-12-31", "2020-06-30", "2024-12-31"]:
            row = gsw.loc[date]
            for t in (1, 5, 10, 30):
                ours = nss_yield(t, row["BETA0"], row["BETA1"], row["BETA2"],
                                 row["BETA3"], row["TAU1"], row["TAU2"])
                assert ours == pytest.approx(row[f"SVENY{t:02d}"], abs=0.015), (date, t)

    def test_curve_from_gsw_row_prices_sanely(self, gsw):
        row = gsw.loc["2024-12-31"]
        curve = DiscountCurve.from_gsw_row(row)
        assert 0.5 < bond_price(0.04, 10, curve) < 1.2
        assert curve.forward(5, 10) > 0


class TestLittermanScheinkman:
    def test_three_factors_explain_the_real_curve(self, gsw):
        """Litterman-Scheinkman (1991) on 35 years of real month-end curves:
        level/slope/curvature explain >95% of yield-change variance."""
        yields = gsw[[f"SVENY{t:02d}" for t in (1, 2, 3, 5, 7, 10, 20, 30)]].dropna()
        loadings, explained = pca_level_slope_curvature(yields)
        assert explained.sum() > 0.95
        assert explained[0] > 0.60  # level dominates
        # level: same sign everywhere; slope: monotone-ish, ends differ in sign
        assert (loadings["PC1"] > 0).all()
        assert loadings["PC2"].iloc[0] * loadings["PC2"].iloc[-1] < 0
