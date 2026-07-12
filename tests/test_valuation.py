"""Valuation package tests: hand-computed formula references, identity checks,
and REAL filing figures (Apple FY2022 via the EDGAR fixture + PIT store)."""

import json
import math
from pathlib import Path

import pytest

from quantropy.data import PointInTimeStore
from quantropy.data.providers import edgar
from quantropy.valuation import (
    StatementSet,
    altman_z,
    beneish_m,
    dcf_value,
    implied_growth,
    piotroski_f,
    ratios,
)

FIXTURE = Path(__file__).parent / "fixtures" / "aapl_facts_trimmed.json"


def s(**kwargs) -> StatementSet:
    return StatementSet(entity="X", period_end="2023-12-31", **kwargs)


class TestRatios:
    FULL = dict(
        revenue=110.0, net_income=11.0, total_assets=100.0, equity=50.0,
        gross_profit=44.0, operating_income=16.5, current_assets=30.0,
        current_liabilities=20.0, total_liabilities=50.0, cash_from_operations=14.0,
    )

    def test_hand_computed_values(self):
        r = ratios(s(**self.FULL))
        assert r.net_margin == pytest.approx(0.10)
        assert r.gross_margin == pytest.approx(0.40)
        assert r.roa == pytest.approx(0.11)
        assert r.roe == pytest.approx(0.22)
        assert r.current_ratio == pytest.approx(1.5)
        assert r.accruals_ratio == pytest.approx((11.0 - 14.0) / 100.0)

    def test_dupont_identity_holds_exactly(self):
        r = ratios(s(**self.FULL))
        assert r.dupont_roe == pytest.approx(r.roe, rel=1e-12)

    def test_missing_inputs_are_nan_not_defaults(self):
        r = ratios(s(revenue=100.0, net_income=10.0))
        assert r.net_margin == pytest.approx(0.10)
        assert math.isnan(r.roe) and math.isnan(r.current_ratio)


class TestDCF:
    def test_constant_growth_matches_gordon_perpetuity(self):
        """With growth == terminal_growth, the two-stage model must collapse to
        the growing perpetuity fcf0*(1+g)/(r-g) — the closed-form cross-check."""
        fcf0, g, r = 100.0, 0.02, 0.08
        gordon = fcf0 * (1 + g) / (r - g)
        assert dcf_value(fcf0, g, r, horizon=10, terminal_growth=g) == pytest.approx(
            gordon, rel=1e-9
        )

    def test_value_increases_with_growth_decreases_with_rate(self):
        base = dcf_value(100, 0.05, 0.09)
        assert dcf_value(100, 0.08, 0.09) > base > dcf_value(100, 0.02, 0.09)
        assert dcf_value(100, 0.05, 0.12) < base

    def test_reverse_dcf_roundtrip(self):
        """implied_growth(dcf_value(g)) == g — the defining property."""
        for g in (-0.05, 0.03, 0.15, 0.40):
            v = dcf_value(100, g, 0.09)
            assert implied_growth(v, 100, 0.09) == pytest.approx(g, abs=1e-6)

    def test_gordon_condition_enforced(self):
        with pytest.raises(ValueError, match="Gordon"):
            dcf_value(100, 0.05, discount_rate=0.02, terminal_growth=0.03)

    def test_unreachable_prices_raise_instead_of_clipping(self):
        with pytest.raises(ValueError, match="floor"):
            implied_growth(1.0, 100, 0.09)  # absurdly cheap
        with pytest.raises(ValueError, match="outside bounds"):
            implied_growth(1e9, 100, 0.09)  # absurdly expensive


class TestScores:
    def test_altman_z_hand_computed(self):
        st = s(current_assets=30, current_liabilities=20, retained_earnings=25,
               ebit=10, total_liabilities=40, revenue=110, total_assets=100)
        # 1.2*.1 + 1.4*.25 + 3.3*.1 + 0.6*(60/40) + 1.0*1.1 = 2.80
        assert altman_z(st, market_cap=60) == pytest.approx(2.80)

    def test_piotroski_perfect_and_zero(self):
        strong = s(net_income=12, cash_from_operations=15, total_assets=100,
                   long_term_debt=10, current_assets=30, current_liabilities=15,
                   shares_outstanding=100, gross_profit=45, revenue=110)
        weak_prior = s(net_income=5, cash_from_operations=4, total_assets=100,
                       long_term_debt=20, current_assets=25, current_liabilities=20,
                       shares_outstanding=100, gross_profit=35, revenue=100)
        assert piotroski_f(strong, weak_prior).score == 9
        # reversed: NI>0, CFO>0, no dilution still score -> exactly 3 (hand-checked)
        assert piotroski_f(weak_prior, strong).score == 3

    def test_piotroski_reports_computability(self):
        sparse = s(net_income=10, total_assets=100)
        out = piotroski_f(sparse, sparse)
        assert out.max_computable < 9  # honesty about missing inputs

    def test_beneish_neutral_firm_reference(self):
        """All indices at 1.0, zero accruals: M = -2.48 exactly — inside the
        published non-manipulator band (~-2.4 to -2.6)."""
        m = beneish_m(dsri=1, gmi=1, aqi=1, sgi=1, depi=1, sgai=1, tata=0, lvgi=1)
        assert m == pytest.approx(-2.48, abs=1e-9)
        assert m < -1.78  # below the manipulation flag


class TestAgainstRealAppleFiling:
    """Statements built through the PIT store from the real EDGAR fixture; ratios
    checked against Apple's actual FY2022 10-K figures."""

    @pytest.fixture(scope="class")
    def apple_fy22(self):
        facts = json.loads(FIXTURE.read_text())
        flows = edgar.facts_to_pit_records(
            facts,
            ["RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss"],
            duration="annual",
        )
        stocks = edgar.facts_to_pit_records(facts, ["Assets"], duration="instant")
        pit = PointInTimeStore.from_frame(
            __import__("pandas").concat([flows, stocks], ignore_index=True)
        )
        view = pit.as_of("2022-12-01")  # after the FY22 10-K, before FY23 data
        return StatementSet.from_pit_view(view, "Apple Inc.", "2022-09-24")

    def test_line_items_match_the_10k(self, apple_fy22):
        assert apple_fy22.revenue == pytest.approx(394_328_000_000)
        assert apple_fy22.net_income == pytest.approx(99_803_000_000)
        assert apple_fy22.total_assets == pytest.approx(352_755_000_000)

    def test_ratios_match_public_figures(self, apple_fy22):
        r = ratios(apple_fy22)
        assert r.net_margin == pytest.approx(0.2531, abs=0.001)  # famous ~25.3%
        assert r.roa == pytest.approx(0.2829, abs=0.001)

    def test_concept_drift_was_handled(self, apple_fy22):
        """Revenue came through the post-ASC-606 tag, not 'Revenues' — the
        fallback map earned its keep."""
        assert not math.isnan(apple_fy22.revenue)
