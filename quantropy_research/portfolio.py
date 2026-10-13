"""KC-27: profile-bound offline allocation and causal funded-return replay."""

from dataclasses import asdict, dataclass
from datetime import datetime
from numbers import Integral
import numpy as np
from .covariance import _observations, ledoit_wolf_identity, sample_covariance

POLICIES = ("equal_weight", "inverse_volatility", "sample_gmv", "lw_identity_gmv")


@dataclass(frozen=True)
class ResearchProfile:
    user_role: str
    mandate_id: str
    account_profile_id: str
    deployment: str
    currency: str
    period_label: str
    permitted_labels: tuple
    max_weight: float
    cost_bps: float
    allocation_basis: str

    def validate(self, labels):
        if self.user_role not in ("owner", "trader", "researcher", "portfolio_manager"):
            raise ValueError("Unknown user role")
        if self.deployment != "offline" or self.allocation_basis != "funded_total_return":
            raise ValueError("Only offline funded total-return profiles are implemented")
        if not all(isinstance(v, str) and v.strip() for v in
                   (self.mandate_id, self.account_profile_id, self.currency, self.period_label)):
            raise ValueError("Explicit mandate, account, currency and period labels required")
        if (not labels or any(not isinstance(v, str) or not v.strip() for v in labels)
                or len(set(labels)) != len(labels) or not set(labels) <= set(self.permitted_labels)):
            raise ValueError("Distinct permitted stream labels required")
        if not np.isfinite(self.max_weight) or not 0 < self.max_weight <= 1:
            raise ValueError("max_weight must be in (0,1]")
        if len(labels) * self.max_weight < 1 - 1e-12:
            raise ValueError("Infeasible fully invested concentration cap")
        if not np.isfinite(self.cost_bps) or not 0 <= self.cost_bps < 10000:
            raise ValueError("cost_bps must be in [0,10000)")


def _project(values, cap):
    """Euclidean projection onto sum(w)=1, 0<=w<=cap by scalar bisection."""
    low, high = float(np.min(values) - cap), float(np.max(values))
    for _ in range(80):
        middle = (low + high) / 2
        weights = np.clip(values - middle, 0, cap)
        if weights.sum() > 1:
            low = middle
        else:
            high = middle
    return np.clip(values - (low + high) / 2, 0, cap)


def _linear_minimum(gradient, cap):
    remaining = 1.0
    value = 0.0
    for index in np.argsort(gradient, kind="stable"):
        weight = min(cap, remaining)
        value += weight * gradient[index]
        remaining -= weight
        if remaining <= 1e-14:
            break
    return value


def _gmv(covariance, cap, tolerance=1e-10, max_iterations=20000):
    """Projected gradient for convex GMV, with a feasible-set objective gap."""
    eigenvalues = np.linalg.eigvalsh(covariance)
    scale = float(eigenvalues[-1])
    if scale <= 0 or eigenvalues[0] < -1e-12 * scale:
        raise ValueError("GMV requires nonzero positive semidefinite covariance")
    matrix = covariance / scale
    weights = np.full(len(matrix), 1 / len(matrix))
    for iteration in range(max_iterations + 1):
        gradient = 2 * matrix @ weights
        gap = max(0.0, float(gradient @ weights - _linear_minimum(gradient, cap)))
        if gap <= tolerance:
            return weights, {"iterations": iteration, "normalized_objective_gap": gap}
        if iteration == max_iterations:
            break
        weights = _project(weights - gradient / 2, cap)
    raise ValueError("GMV did not converge; no fallback allocation is returned")


def allocate(training, policy, max_weight):
    x = _observations(training)
    p = x.shape[1]
    if not np.isfinite(max_weight) or not 0 < max_weight <= 1 or p * max_weight < 1 - 1e-12:
        raise ValueError("Infeasible concentration cap")
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    diagnostics = {"policy": policy, "training_observations": len(x)}
    if policy == "equal_weight":
        return np.full(p, 1 / p), diagnostics
    if policy == "lw_identity_gmv":
        estimate = ledoit_wolf_identity(x)
        covariance = estimate.covariance
        diagnostics["shrinkage"] = estimate.shrinkage
    else:
        covariance = sample_covariance(x)
    if policy == "inverse_volatility":
        variances = np.diag(covariance)
        if np.any(variances <= 0):
            raise ValueError("Inverse volatility requires positive sample variances")
        inverse = 1 / np.sqrt(variances)
        raw = inverse / inverse.sum()
        weights = _project(raw, max_weight)
        diagnostics["cap_projection_applied"] = bool(np.any(raw > max_weight))
    else:
        weights, convergence = _gmv(covariance, max_weight)
        diagnostics.update(convergence)
    if (not np.isfinite(weights).all() or abs(weights.sum() - 1) > 1e-9
            or np.min(weights) < -1e-10 or np.max(weights) > max_weight + 1e-9):
        raise ValueError("Allocation failed feasibility verification")
    diagnostics["estimated_period_variance"] = float(weights @ covariance @ weights)
    return weights, diagnostics


def _time(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Timestamps must include a timezone")
    return result


def _rebalance(previous, target, cost_rate):
    """Solve q + c sum(abs(q*w-h)) = 1, including initial cash funding."""
    low, high = 0.0, 1.0
    for _ in range(80):
        q = (low + high) / 2
        traded = float(np.sum(np.abs(q * target - previous)))
        if q + cost_rate * traded > 1:
            high = q
        else:
            low = q
    q = (low + high) / 2
    traded = float(np.sum(np.abs(q * target - previous)))
    if abs(q + cost_rate * traded - 1) > 1e-10:
        raise ValueError("Self-financing rebalance failed reconciliation")
    return q, traded


def compare_policies(dataset, profile, lookback, policies=POLICIES):
    """Evaluate predeclared policies on common intervals; raise on any failure.

    Returns must describe fully funded, investable total-return streams in one
    currency, with explicit start/end/availability timestamps. No price fills,
    derivative margin, taxes, short positions, or order adapters are modeled.
    """
    labels = dataset["labels"]
    profile.validate(labels)
    if dataset["currency"] != profile.currency or dataset["period_label"] != profile.period_label:
        raise ValueError("Dataset/profile units differ")
    if dataset["allocation_basis"] != profile.allocation_basis:
        raise ValueError("Dataset/profile allocation basis differs")
    if not isinstance(dataset.get("provenance"), str) or not dataset["provenance"].strip():
        raise ValueError("Data provenance required")
    if isinstance(lookback, bool) or not isinstance(lookback, Integral) or lookback < 2:
        raise ValueError("lookback must be an integer >=2")
    policies = tuple(policies)
    if not policies or len(set(policies)) != len(policies) or not set(policies) <= set(POLICIES):
        raise ValueError("Distinct declared policies required")
    records = dataset["records"]
    returns = _observations([r["returns"] for r in records])
    if returns.shape[1] != len(labels) or np.any(returns < -1):
        raise ValueError("Return dimensions or funded-return domain invalid")
    starts = [_time(r["start"]) for r in records]
    ends = [_time(r["end"]) for r in records]
    availability = [_time(r["available_at"]) for r in records]
    for i in range(len(records)):
        if starts[i] >= ends[i] or availability[i] < ends[i]:
            raise ValueError("Return cannot be known before its interval ends")
        if i and starts[i] != ends[i-1]:
            raise ValueError("Require ordered contiguous nonoverlapping return intervals")
    state = {policy: {"wealth": 1.0, "holdings": np.zeros(len(labels)), "steps": []}
             for policy in policies}
    for t in range(len(records)):
        eligible = [j for j in range(t) if ends[j] <= starts[t] and availability[j] <= starts[t]]
        if len(eligible) < lookback:
            continue
        training_indices = eligible[-lookback:]
        training = returns[training_indices]
        for policy in policies:
            item = state[policy]
            weights, diagnostics = allocate(training, policy, profile.max_weight)
            q, traded = _rebalance(item["holdings"], weights, profile.cost_bps / 10000)
            gross = float(weights @ returns[t])
            wealth_multiplier = q * (1 + gross)
            if not np.isfinite(wealth_multiplier) or wealth_multiplier <= 0:
                raise ValueError("Portfolio exhausted or return outside floating-point range")
            item["wealth"] *= wealth_multiplier
            if not np.isfinite(item["wealth"]) or item["wealth"] <= 0:
                raise ValueError("Wealth outside floating-point range")
            item["holdings"] = weights * (1 + returns[t]) / (1 + gross)
            item["steps"].append({
                "decision_at": records[t]["start"], "return_end": records[t]["end"],
                "training_indices": training_indices, "target_weights": weights.tolist(),
                "gross_return": gross, "net_return": wealth_multiplier - 1,
                "traded_notional_fraction": traded, "cost_fraction": 1 - q,
                "wealth": item["wealth"], "diagnostics": diagnostics})
    if not any(item["steps"] for item in state.values()):
        raise ValueError("No evaluation interval has enough available history")
    summaries = {}
    for policy, item in state.items():
        steps = item["steps"]
        net = np.array([step["net_return"] for step in steps])
        path = np.array([1.0] + [step["wealth"] for step in steps])
        summaries[policy] = {"terminal_wealth": item["wealth"],
            "net_compound_return": item["wealth"] - 1, "evaluation_periods": len(steps),
            "period_mean_net_return": float(net.mean()),
            "period_sample_volatility": float(net.std(ddof=1)) if len(net) > 1 else None,
            "maximum_drawdown": float(np.max(1 - path / np.maximum.accumulate(path))),
            "total_traded_notional_fraction": sum(s["traded_notional_fraction"] for s in steps),
            "steps": steps}
    return {"schema_version": 1, "profile": asdict(profile), "labels": list(labels),
            "lookback": int(lookback), "provenance": dataset["provenance"],
            "scope": "Offline funded-return comparison; no empirical or live certification",
            "policies": summaries}
