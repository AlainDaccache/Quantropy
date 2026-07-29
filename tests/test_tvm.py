"""Reference tests for quantropy.core.tvm (P2: money math gets adversarial coverage).

Two layers: (1) hardcoded reference values computed independently of the library,
(2) brute-force cash-flow consistency — every closed form must equal the explicit
period-by-period loop it summarizes.
"""

import pytest

from quantropy.core import tvm


class TestFutureValue:
    def test_single_cash_flow_reference(self):
        # 1000 at 5% for 10 periods = 1628.8946267774414
        assert tvm.future_value(1000, 0.05, 10) == pytest.approx(1628.8946267774414)

    def test_rate_path(self):
        # 100 * 1.10 * 0.95 = 104.5
        assert tvm.future_value(100, [0.10, -0.05]) == pytest.approx(104.5)

    def test_rate_path_and_periods_is_an_error(self):
        with pytest.raises(ValueError):
            tvm.future_value(100, [0.05], periods=10)

    def test_scalar_rate_requires_periods(self):
        with pytest.raises(ValueError):
            tvm.future_value(100, 0.05)

    def test_present_value_inverts_future_value(self):
        fv = tvm.future_value(1000, 0.07, 15)
        assert tvm.present_value(fv, 0.07, 15) == pytest.approx(1000)


def brute_force_fv_annuity(contribution, rate, periods, growth=0.0, pv=0.0, due=False):
    """Explicit simulation: contribute each period (growing), compound the balance."""
    balance = pv
    for t in range(periods):
        pay = contribution * (1 + growth) ** t
        if due:  # payment at period start: deposit, then the period's growth applies
            balance = (balance + pay) * (1 + rate)
        else:  # payment at period end: grow the balance, then deposit
            balance = balance * (1 + rate) + pay
    return balance


class TestFutureValueAnnuity:
    def test_level_ordinary_reference(self):
        # 100/period, 5%, 10 periods: 100 * (1.05^10 - 1)/0.05 = 1257.7892535548839
        assert tvm.future_value_annuity(100, 0.05, 10) == pytest.approx(1257.7892535548839)

    def test_level_due_reference(self):
        # ordinary * 1.05 = 1320.678716...
        assert tvm.future_value_annuity(100, 0.05, 10, due=True) == pytest.approx(
            1320.6787162326282
        )

    def test_growing_reference(self):
        # 8000, r=3%, g=6%, n=10 -> 119181.68458632865 (legacy example, now verified)
        assert tvm.future_value_annuity(8000, 0.03, 10, growth=0.06) == pytest.approx(
            119181.68458632865
        )

    def test_rate_equals_growth_limit(self):
        # r == g: FV = C * n * (1+r)^(n-1) = 100*10*1.05^9 = 1551.3282073589796
        assert tvm.future_value_annuity(100, 0.05, 10, growth=0.05) == pytest.approx(
            1551.3282073589796
        )

    @pytest.mark.parametrize("due", [False, True])
    @pytest.mark.parametrize(
        "contribution,rate,periods,growth,pv",
        [
            (100, 0.05, 10, 0.0, 0.0),
            (100, 0.05, 10, 0.0, 500.0),
            (8000, 0.03, 10, 0.06, 0.0),
            (250, 0.07, 30, 0.02, 10_000.0),
            (100, 0.05, 10, 0.05, 0.0),  # r == g limit
            (100, 0.04, 1, 0.0, 0.0),  # single period
        ],
    )
    def test_matches_brute_force(self, contribution, rate, periods, growth, pv, due):
        closed = tvm.future_value_annuity(contribution, rate, periods, growth, pv, due)
        brute = brute_force_fv_annuity(contribution, rate, periods, growth, pv, due)
        assert closed == pytest.approx(brute)


def brute_force_pv_annuity(payment, rate, periods, growth=0.0, due=False):
    """Explicit discounting of each (growing) payment."""
    total = 0.0
    for t in range(1, periods + 1):
        pay = payment * (1 + growth) ** (t - 1)
        when = t - 1 if due else t
        total += pay / (1 + rate) ** when
    return total


class TestPresentValueAnnuity:
    def test_level_ordinary_reference(self):
        # 100/period, 5%, 10 periods: 100 * (1 - 1.05^-10)/0.05 = 772.1734929184818
        assert tvm.present_value_annuity(100, 0.05, 10) == pytest.approx(772.1734929184818)

    @pytest.mark.parametrize("due", [False, True])
    @pytest.mark.parametrize(
        "payment,rate,periods,growth",
        [
            (100, 0.05, 10, 0.0),
            (100, 0.08, 20, 0.03),
            (100, 0.05, 10, 0.05),  # r == g limit
            (1000, 0.10, 1, 0.0),
        ],
    )
    def test_matches_brute_force(self, payment, rate, periods, growth, due):
        closed = tvm.present_value_annuity(payment, rate, periods, growth, due)
        brute = brute_force_pv_annuity(payment, rate, periods, growth, due)
        assert closed == pytest.approx(brute)


class TestPerpetuity:
    def test_gordon_reference(self):
        # 100 / (0.08 - 0.03) = 2000
        assert tvm.present_value_perpetuity(100, 0.08, 0.03) == pytest.approx(2000.0)

    def test_rate_must_exceed_growth(self):
        with pytest.raises(ValueError):
            tvm.present_value_perpetuity(100, 0.03, 0.03)
