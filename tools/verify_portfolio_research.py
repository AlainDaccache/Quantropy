"""Recompute committed offline demonstration; optionally compare pinned source.

The optional source is NOT imported as a library. Only the reviewed, hash-pinned
ledoit_wolf_shrinkage function is extracted; decorators are removed. This checks
the reference numerical routine, not a full scikit-learn installation.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import warnings
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from quantropy_research.__main__ import run_file
from quantropy_research.covariance import ledoit_wolf_identity

KB = REPO / "docs" / "knowledge-base"
REFERENCE_SHA256 = "e25d87f453b331b75452c3956832dd7d68eadd7a22df97a970482e534b90cc9e"


def assert_report_close(actual, recorded, path="root"):
    if isinstance(actual, dict):
        if set(actual) != set(recorded):
            raise AssertionError("Evidence keys differ at " + path)
        for key in actual:
            # Environment metadata records the generating runtime, not a universal prerequisite.
            if path == "root.reproducibility" and key in ("python", "numpy"):
                continue
            assert_report_close(actual[key], recorded[key], path + "." + key)
    elif isinstance(actual, (tuple, list)):
        if len(actual) != len(recorded):
            raise AssertionError("Evidence lengths differ at " + path)
        for index, (a, b) in enumerate(zip(actual, recorded)):
            assert_report_close(a, b, path + f"[{index}]")
    elif isinstance(actual, float):
        if not np.isclose(actual, recorded, rtol=1e-8, atol=1e-10):
            raise AssertionError("Evidence value differs at " + path)
    elif actual != recorded:
        raise AssertionError("Evidence value differs at " + path)


def compare_reference(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA256:
        raise ValueError("Reference must be the inspected scikit-learn 1.7.2 source bytes")
    tree = ast.parse(raw.decode("utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "ledoit_wolf_shrinkage")
    function.decorator_list = []
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"np": np, "warnings": warnings, "check_array": lambda x: np.asarray(x, dtype=float)}
    exec(compile(module, "pinned_reference", "exec"), namespace)
    reference = namespace["ledoit_wolf_shrinkage"]
    rng = np.random.default_rng(172)
    cases = [np.array([[1, 0], [-1, 0], [0, 2], [0, -2]], dtype=float),
             np.zeros((5, 3)), np.ones((5, 3)), np.array([[1], [2], [3]], dtype=float),
             np.array([[1, 0], [-1, 0], [0, 1], [0, -1]], dtype=float)]
    for n, p in [(2, 2), (5, 12), (20, 3), (100, 10)]:
        for _ in range(20):
            x = rng.normal(size=(n, p)) * np.linspace(.1, 2, p) + .5
            cases.append(x)
    max_covariance_error = max_intensity_error = 0.0
    for x in cases:
        delta = float(reference(x, block_size=3))
        centered = x - x.mean(axis=0)
        s = centered.T @ centered / len(x)
        expected = (1-delta)*s + delta*np.trace(s)/x.shape[1]*np.eye(x.shape[1])
        actual = ledoit_wolf_identity(x)
        np.testing.assert_allclose(actual.covariance, expected, rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(actual.shrinkage, delta, rtol=1e-10, atol=1e-12)
        max_covariance_error = max(max_covariance_error, float(np.max(np.abs(actual.covariance-expected))))
        max_intensity_error = max(max_intensity_error, abs(actual.shrinkage-delta))
    return {"reference_url": "https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.7.2/sklearn/covariance/_shrunk_covariance.py",
            "reference_sha256": REFERENCE_SHA256, "reference_function": "ledoit_wolf_shrinkage",
            "implementation_sha256": hashlib.sha256((REPO / "quantropy_research/covariance.py").read_bytes()).hexdigest(),
            "fixtures": len(cases), "seed": 172, "passed": True,
            "maximum_covariance_absolute_error": max_covariance_error,
            "maximum_intensity_absolute_error": max_intensity_error,
            "scope": "Author-run extracted pinned numerical function comparison; validation wrapper and full installed package not executed; no empirical or expert certification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-source", type=Path)
    parser.add_argument("--write-reference-evidence", action="store_true")
    args = parser.parse_args()
    if args.write_reference_evidence and args.reference_source is None:
        parser.error("Writing reference evidence requires the inspected reference source")
    actual = run_file(REPO / "examples" / "portfolio-comparison.json")
    recorded = json.loads((KB / "portfolio-comparison-verification.json").read_text(encoding="utf-8"))
    assert_report_close(actual, recorded)
    recorded_reference = json.loads((KB / "portfolio-reference-verification.json").read_text(encoding="utf-8"))
    if (recorded_reference["reference_sha256"] != REFERENCE_SHA256
            or recorded_reference.get("implementation_sha256") != hashlib.sha256(
                (REPO / "quantropy_research/covariance.py").read_bytes()).hexdigest()
            or recorded_reference["passed"] is not True):
        if not args.write_reference_evidence:
            raise AssertionError("Reference evidence hash/status is stale")
    if args.reference_source:
        evidence = compare_reference(args.reference_source)
        if args.write_reference_evidence:
            (KB / "portfolio-reference-verification.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            assert_report_close(evidence, recorded_reference)
        print(json.dumps(evidence, indent=2))
    print(json.dumps({"comparison_report": "recomputed and matched", "policies": len(actual["policies"]),
                      "reference_comparison": "rerun" if args.reference_source else "recorded hashes checked; not rerun",
                      "periods_per_policy": next(iter(actual["policies"].values()))["evaluation_periods"]}, indent=2))


if __name__ == "__main__":
    main()
