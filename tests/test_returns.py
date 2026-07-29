"""Reference tests for quantropy.core.returns."""

import numpy as np
import pytest

from quantropy.core import returns as ret


class TestConversions:
    def test_to_log_reference(self):
        # ln(1.10) = 0.09531017980432486
        assert ret.to_log(0.10) == pytest.approx(0.09531017980432486)

    def test_roundtrip(self):
        r = np.array([-0.05, 0.0, 0.02, 0.10])
        assert ret.to_simple(ret.to_log(r)) == pytest.approx(r)

    def test_log_returns_add_where_simple_compound(self):
        simple = np.array([0.10, -0.05, 0.03])
        total_from_logs = float(np.expm1(ret.to_log(simple).sum()))
        assert total_from_logs == pytest.approx(ret.cumulative_return(simple))


class TestCumulative:
    def test_reference(self):
        # 1.1 * 0.9 - 1 = -0.01 (the classic +10%/-10% asymmetry)
        assert ret.cumulative_return([0.10, -0.10]) == pytest.approx(-0.01)


class TestAnnualization:
    def test_geometric_reference(self):
        # 1% monthly, geometric: 1.01^12 - 1 = 0.12682503013196977
        assert ret.annualize_return(0.01, 12) == pytest.approx(0.12682503013196977)

    def test_arithmetic(self):
        assert ret.annualize_return(0.01, 12, geometric=False) == pytest.approx(0.12)

    def test_volatility_sqrt_time(self):
        # 1% daily vol: 0.01 * sqrt(252) = 0.15874507866387544
        assert ret.annualize_volatility(0.01, 252) == pytest.approx(0.15874507866387544)


class TestCagr:
    def test_doubling_in_ten_years(self):
        # 2^(1/10) - 1 = 0.07177346253629313
        assert ret.cagr(2.0, 10) == pytest.approx(0.07177346253629313)

    @pytest.mark.parametrize("growth,years", [(0.0, 10), (-1.0, 10), (2.0, 0)])
    def test_invalid_inputs_raise(self, growth, years):
        with pytest.raises(ValueError):
            ret.cagr(growth, years)
