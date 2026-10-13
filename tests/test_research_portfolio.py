"""Numerical and economic checks; deliberately avoid importing the legacy app."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest
import numpy as np
from quantropy_research import ResearchProfile, allocate, compare_policies
from quantropy_research.covariance import ledoit_wolf_identity, sample_covariance
from quantropy_research.portfolio import _gmv, _rebalance


def fixture():
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    records = []
    for i in range(18):
        end = start + timedelta(days=1)
        records.append({"start": start.isoformat(), "end": end.isoformat(),
                        "available_at": end.isoformat(),
                        "returns": [.01*((i % 3)-1), .005*((i % 5)-2), .002*((i % 7)-3)]})
        start = end
    dataset = {"labels": ["A", "B", "C"], "currency": "SCENARIO",
               "period_label": "one_day_synthetic", "allocation_basis": "funded_total_return",
               "provenance": "Fictional arithmetic fixture; not market observations", "records": records}
    profile = ResearchProfile("researcher", "synthetic-risk-comparison", "scenario-account",
                              "offline", "SCENARIO", "one_day_synthetic", ("A", "B", "C"),
                              .6, 10, "funded_total_return")
    return dataset, profile


class CovarianceTests(unittest.TestCase):
    def test_hand_calculated_partial_shrinkage(self):
        # Zero means; n=4, S=diag(.5,2), mu=1.25,
        # distance=.5625, noise=.53125, delta=17/18.
        x = [[1, 0], [-1, 0], [0, 2], [0, -2]]
        result = ledoit_wolf_identity(x)
        self.assertAlmostEqual(result.shrinkage, 17/18)
        np.testing.assert_allclose(result.covariance, np.diag([29/24, 31/24]))
        np.testing.assert_allclose(sample_covariance(x), np.diag([2/3, 8/3]))

    def test_degenerate_domains(self):
        for x in [np.zeros((3, 2)), np.full((3, 2), 4)]:
            result = ledoit_wolf_identity(x)
            np.testing.assert_array_equal(result.covariance, np.zeros((2, 2)))
            self.assertEqual(result.shrinkage, 0)
        result = ledoit_wolf_identity([[1], [2], [3]])
        self.assertEqual(result.shrinkage, 0)
        self.assertAlmostEqual(result.covariance[0, 0], 2/3)

    def test_translation_scale_permutation_and_psd(self):
        rng = np.random.default_rng(7)
        x = rng.normal(size=(7, 12))
        result = ledoit_wolf_identity(x)
        np.testing.assert_allclose(ledoit_wolf_identity(x+2).covariance, result.covariance, atol=1e-14)
        np.testing.assert_allclose(ledoit_wolf_identity(100*x).covariance, 10000*result.covariance)
        np.testing.assert_allclose(ledoit_wolf_identity(x[:, ::-1]).covariance,
                                   result.covariance[::-1, ::-1])
        self.assertGreater(np.linalg.eigvalsh(result.covariance)[0], 0)
        self.assertAlmostEqual(np.trace(result.covariance), np.trace(np.cov(x, rowvar=False, bias=True)))

    def test_identity_scatter(self):
        result = ledoit_wolf_identity([[1, 0], [-1, 0], [0, 1], [0, -1]])
        np.testing.assert_allclose(result.covariance, .5*np.eye(2))
        self.assertEqual(result.shrinkage, 0)

    def test_reject_invalid_observations(self):
        for x in [[[1, 2]], [[1, np.nan], [2, 3]], [1, 2], [[], []],
                  [[1e200, 0], [-1e200, 0]], [[1e-200], [-1e-200]]]:
            with self.subTest(x=x), self.assertRaises(ValueError):
                ledoit_wolf_identity(x)


class PolicyTests(unittest.TestCase):
    def test_analytic_diagonal_gmv(self):
        weights, diagnostics = _gmv(np.diag([.01, .04]), 1)
        np.testing.assert_allclose(weights, [.8, .2], atol=2e-10)
        self.assertLessEqual(diagnostics["normalized_objective_gap"], 1e-10)

    def test_cap_and_scale(self):
        expected = [.6, .4]
        for scale in (1e-10, 1, 1e10):
            np.testing.assert_allclose(_gmv(scale*np.diag([.01, .04]), .6)[0], expected, atol=1e-10)

    def test_correlated_boundary_solution(self):
        # Unconstrained two-asset optimum exceeds one, so long-only chooses A.
        np.testing.assert_allclose(_gmv(np.array([[1., 2.], [2., 9.]]), 1)[0], [1, 0], atol=1e-10)

    def test_three_asset_grid_lower_bound(self):
        covariance = np.array([[1, .2, -.1], [.2, 2, .4], [-.1, .4, 3.]])
        weights, _ = _gmv(covariance, .6)
        value = weights @ covariance @ weights
        for i in range(61):
            for j in range(61):
                candidate = np.array([i/100, j/100, 1-(i+j)/100])
                if np.min(candidate) >= 0 and np.max(candidate) <= .6:
                    self.assertLessEqual(value, candidate @ covariance @ candidate + 1e-9)

    def test_solver_failure_and_covariance_domains(self):
        with self.assertRaises(ValueError):
            _gmv(np.diag([1., 4.]), 1, max_iterations=0)
        for matrix in (np.zeros((2, 2)), np.diag([-1., 2.])):
            with self.assertRaises(ValueError):
                _gmv(matrix, 1)

    def test_inverse_volatility_and_cap(self):
        x = [[1, 0], [-1, 0], [0, 2], [0, -2]]
        np.testing.assert_allclose(allocate(x, "inverse_volatility", 1)[0], [2/3, 1/3])
        weights, diagnostics = allocate(x, "inverse_volatility", .6)
        np.testing.assert_allclose(weights, [.6, .4])
        self.assertTrue(diagnostics["cap_projection_applied"])
        with self.assertRaises(ValueError):
            allocate(np.ones((4, 2)), "inverse_volatility", 1)


class ReplayTests(unittest.TestCase):
    def test_cost_funding_and_drift_hand_case(self):
        q, traded = _rebalance(np.zeros(2), np.array([.5, .5]), .01)
        self.assertAlmostEqual(q, 1/1.01)
        self.assertAlmostEqual(traded, q)
        # Existing holdings have drifted to 60/40; exact cost is .002,
        # buys and sells total .2 of pretrade wealth, not half turnover.
        q, traded = _rebalance(np.array([.6, .4]), np.array([.5, .5]), .01)
        self.assertAlmostEqual(q, .998)
        self.assertAlmostEqual(traded, .2)
        self.assertAlmostEqual(q + .01*traded, 1)

    def test_prefix_causality_and_future_perturbation(self):
        data, profile = fixture()
        baseline = compare_policies(data, profile, 5)
        changed = deepcopy(data)
        changed["records"][-1]["returns"] = [.9, -.7, .1]
        altered = compare_policies(changed, profile, 5)
        prefix = deepcopy(data)
        prefix["records"] = prefix["records"][:-1]
        shorter = compare_policies(prefix, profile, 5)
        for policy in baseline["policies"]:
            a = baseline["policies"][policy]["steps"]
            b = altered["policies"][policy]["steps"]
            self.assertEqual(a[:-1], b[:-1])
            self.assertEqual(a[-1]["target_weights"], b[-1]["target_weights"])
            self.assertEqual(a[:-1], shorter["policies"][policy]["steps"])

    def test_availability_not_observation_time(self):
        data, profile = fixture()
        data["records"][4]["available_at"] = data["records"][8]["start"]
        result = compare_policies(data, profile, 4, ("equal_weight",))
        steps = result["policies"]["equal_weight"]["steps"]
        before = next(s for s in steps if s["decision_at"] == data["records"][6]["start"])
        after = next(s for s in steps if s["decision_at"] == data["records"][8]["start"])
        self.assertNotIn(4, before["training_indices"])
        self.assertIn(4, after["training_indices"])

    def test_common_intervals_and_wealth_reconciliation(self):
        data, profile = fixture()
        result = compare_policies(data, profile, 5)
        dates = []
        for policy in result["policies"].values():
            dates.append([s["decision_at"] for s in policy["steps"]])
            self.assertAlmostEqual(np.prod([1+s["net_return"] for s in policy["steps"]]),
                                   policy["terminal_wealth"])
        self.assertTrue(all(dates[0] == d for d in dates))

    def test_no_cost_vs_positive_cost(self):
        data, profile = fixture()
        from dataclasses import replace
        free = compare_policies(data, replace(profile, cost_bps=0), 5)
        costly = compare_policies(data, profile, 5)
        for policy in free["policies"]:
            self.assertGreater(free["policies"][policy]["terminal_wealth"],
                               costly["policies"][policy]["terminal_wealth"])

    def test_reject_profiles_and_bad_data(self):
        data, profile = fixture()
        from dataclasses import replace
        for change in ({"deployment": "live"}, {"max_weight": .2}, {"cost_bps": -1},
                       {"permitted_labels": ("A",)}, {"allocation_basis": "futures_notional"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                compare_policies(data, replace(profile, **change), 5)
        for field, value in (("currency", "OTHER"), ("labels", ["A", "A", "C"]),
                             ("provenance", "")):
            changed = deepcopy(data)
            changed[field] = value
            with self.assertRaises(ValueError):
                compare_policies(changed, profile, 5)
        for field, value in (("available_at", data["records"][0]["start"]),
                             ("end", "2020-01-02T00:00:00"), ("returns", [-1.1, 0, 0])):
            changed = deepcopy(data)
            changed["records"][0][field] = value
            with self.assertRaises(ValueError):
                compare_policies(changed, profile, 5)

    def test_total_loss_fails_explicitly(self):
        data, profile = fixture()
        data["records"][5]["returns"] = [-1, -1, -1]
        with self.assertRaises(ValueError):
            compare_policies(data, profile, 5, ("equal_weight",))


if __name__ == "__main__":
    unittest.main()
