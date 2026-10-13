"""Run a local comparison: python -m quantropy_research input.json --output report.json."""

import argparse
from dataclasses import fields
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
from .portfolio import ResearchProfile, compare_policies


def run_file(path):
    raw = Path(path).read_bytes()
    config = json.loads(raw)
    expected = {f.name for f in fields(ResearchProfile)}
    if set(config["profile"]) != expected:
        raise ValueError("Profile fields must match the declared schema exactly")
    profile = ResearchProfile(**config["profile"])
    report = compare_policies(config["dataset"], profile, config["lookback"], config["policies"])
    root = Path(__file__).parent
    report["reproducibility"] = {
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(root.glob("*.py"))},
        "python": platform.python_version(), "numpy": np.__version__,
        "evidence_type": "synthetic numerical demonstration" if config.get("synthetic")
                         else "user-supplied observations; empirical validity unassessed"}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(run_file(args.input), indent=2, allow_nan=False) + "\n"
    if args.output:
        if args.output.resolve() == args.input.resolve():
            parser.error("Output must not overwrite the input")
        args.output.write_text(result, encoding="utf-8", newline="\n")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
