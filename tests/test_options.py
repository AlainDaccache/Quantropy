"""Options tests: Hull's textbook reference values, put-call parity as identity,
Greeks vs bump-and-reprice, tree convergence to BSM, American exercise premium,
implied-vol round-trip."""

import numpy as np
import pytest

from quantropy.pricing import binomial_price, bs_greeks, bs_price, implied_vol

# Hull's classic example (Options, Futures and Other Derivatives):
# S=42, K=40, T=0.5, r=10%, sigma=20%  ->  c = 4.76, p = 0.81
HULL = dict(s=42.0, k=40.0, t=0.5, r=0.10, sigma=0.20)


class TestBlackScholes:
    def test_hull_reference_values(self):
        assert bs_price(**HULL, kind="call") == pytest.approx(4.759, abs=0.001)
        assert bs_price(**HULL, kind="put") == pytest.approx(0.808, abs=0.001)

    def test_put_call_parity_is_an_identity(self):
        for q in (0.0, 0.03):
            c = bs_price(**HULL, kind="call", q=q)
            p = bs_price(**HULL, kind="put", q=q)
            lhs = c - p
            rhs = HULL["s"] * np.exp(-q * HULL["t"]) - HULL["k"] * np.exp(-HULL["r"] * HULL["t"])
            assert lhs == pytest.approx(rhs, abs=1e-12)

    def test_deep_itm_call_approaches_forward_intrinsic(self):
        c = bs_price(s=200, k=40, t=0.5, r=0.10, sigma=0.20, kind="call")
        assert c == pytest.approx(200 - 40 * np.exp(-0.05), abs=1e-6)

    def test_atm_short_dated_rule_of_thumb(self):
        """c_ATM ~ 0.4 * S * sigma * sqrt(T) — the trader's mental-math check."""
        c = bs_price(s=100, k=100, t=0.25, r=0.0, sigma=0.20, kind="call")
        assert c == pytest.approx(0.4 * 100 * 0.20 * np.sqrt(0.25), rel=0.02)

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError):
            bs_price(s=-1, k=40, t=0.5, r=0.1, sigma=0.2)
        with pytest.raises(ValueError):
            bs_price(s=42, k=40, t=0.0, r=0.1, sigma=0.2)


class TestGreeks:
    @pytest.mark.parametrize("kind", ["call", "put"])
    def test_analytic_greeks_match_bump_and_reprice(self, kind):
        """The self-consistency test: every closed-form Greek must equal its
        finite-difference counterpart."""
        g = bs_greeks(**HULL, kind=kind)
        h = 1e-4
        fd_delta = (bs_price(**{**HULL, "s": HULL["s"] + h}, kind=kind)
                    - bs_price(**{**HULL, "s": HULL["s"] - h}, kind=kind)) / (2 * h)
        fd_gamma = (bs_price(**{**HULL, "s": HULL["s"] + h}, kind=kind)
                    - 2 * bs_price(**HULL, kind=kind)
                    + bs_price(**{**HULL, "s": HULL["s"] - h}, kind=kind)) / h**2
        fd_vega = (bs_price(**{**HULL, "sigma": HULL["sigma"] + h}, kind=kind)
                   - bs_price(**{**HULL, "sigma": HULL["sigma"] - h}, kind=kind)) / (2 * h)
        fd_theta = -(bs_price(**{**HULL, "t": HULL["t"] + h}, kind=kind)
                     - bs_price(**{**HULL, "t": HULL["t"] - h}, kind=kind)) / (2 * h)
        fd_rho = (bs_price(**{**HULL, "r": HULL["r"] + h}, kind=kind)
                  - bs_price(**{**HULL, "r": HULL["r"] - h}, kind=kind)) / (2 * h)
        assert g["delta"] == pytest.approx(fd_delta, abs=1e-6)
        assert g["gamma"] == pytest.approx(fd_gamma, abs=1e-4)
        assert g["vega"] == pytest.approx(fd_vega, abs=1e-4)
        assert g["theta"] == pytest.approx(fd_theta, abs=1e-4)
        assert g["rho"] == pytest.approx(fd_rho, abs=1e-4)

    def test_call_put_delta_relationship(self):
        """delta_call - delta_put = e^{-qT} (parity differentiated)."""
        q = 0.02
        dc = bs_greeks(**HULL, kind="call", q=q)["delta"]
        dp = bs_greeks(**HULL, kind="put", q=q)["delta"]
        assert dc - dp == pytest.approx(np.exp(-q * HULL["t"]), abs=1e-12)

    def test_gamma_and_vega_identical_for_calls_and_puts(self):
        gc, gp = (bs_greeks(**HULL, kind=k) for k in ("call", "put"))
        assert gc["gamma"] == pytest.approx(gp["gamma"], abs=1e-12)
        assert gc["vega"] == pytest.approx(gp["vega"], abs=1e-12)


class TestBinomial:
    def test_converges_to_black_scholes(self):
        bsm = bs_price(**HULL, kind="call")
        assert binomial_price(**HULL, kind="call", steps=1000) == pytest.approx(bsm, abs=0.005)

    def test_american_call_no_dividends_equals_european(self):
        """Merton: never exercise an American call on a non-dividend payer early."""
        eu = binomial_price(**HULL, kind="call", style="european", steps=500)
        am = binomial_price(**HULL, kind="call", style="american", steps=500)
        assert am == pytest.approx(eu, abs=1e-9)

    def test_american_put_carries_early_exercise_premium(self):
        eu = binomial_price(**HULL, kind="put", style="european", steps=500)
        am = binomial_price(**HULL, kind="put", style="american", steps=500)
        assert am > eu + 1e-4  # positive premium
        assert am >= HULL["k"] - HULL["s"] - 1e-12  # never below intrinsic

    def test_dividend_yield_lowers_calls_raises_puts(self):
        c0 = binomial_price(**HULL, kind="call", steps=300)
        cq = binomial_price(**HULL, kind="call", steps=300, q=0.05)
        pq = binomial_price(**HULL, kind="put", steps=300, q=0.05)
        p0 = binomial_price(**HULL, kind="put", steps=300)
        assert cq < c0 and pq > p0


class TestImpliedVol:
    def test_roundtrip(self):
        for sigma in (0.08, 0.20, 0.55):
            price = bs_price(**{**HULL, "sigma": sigma}, kind="call")
            assert implied_vol(price, HULL["s"], HULL["k"], HULL["t"], HULL["r"],
                               "call") == pytest.approx(sigma, abs=1e-8)

    def test_arbitrage_violating_price_raises(self):
        with pytest.raises(ValueError, match="achievable range"):
            implied_vol(0.01, **{k: HULL[k] for k in ("s", "k", "t", "r")}, kind="call")
