"""The dependency law, enforced (docs/ARCHITECTURE.md §3).

Parses every module under quantropy/ and asserts each internal import points only
to packages the architecture allows. The diagram in the docs cannot silently rot:
a violating import fails the build with a message naming the edge.
"""

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1] / "quantropy"

# package -> internal packages it may import from (itself is always allowed)
ALLOWED: dict[str, set[str]] = {
    "core": set(),
    "data": {"core"},
    "research": {"core"},
    "portfolio": {"core"},
    "evaluation": {"core"},
    # backtest may consume evaluation's fold DEFINITIONS (walk-forward harness);
    # evaluation still never imports backtest — the judging arrow stays one-way
    "backtest": {"core", "data", "research", "portfolio", "evaluation"},
    "valuation": {"core", "data"},  # M3
    "pricing": {"core", "data"},  # M4/M6
    "risk": {"core", "data", "portfolio"},  # M5
    "live": {"core", "data", "backtest"},
}


def internal_imports(path: Path) -> set[str]:
    """Top-level quantropy subpackages imported by a module."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(
            "quantropy."
        ):
            targets.add(node.module.split(".")[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("quantropy."):
                    targets.add(alias.name.split(".")[1])
    return targets


def test_every_package_is_registered_in_the_law():
    """A new package must declare its allowed dependencies before it exists."""
    packages = {
        p.name
        for p in PACKAGE_ROOT.iterdir()
        if p.is_dir() and (p / "__init__.py").exists()
    }
    unregistered = packages - set(ALLOWED)
    assert not unregistered, (
        f"packages missing from the dependency law: {sorted(unregistered)} — "
        "add them to ALLOWED in this test AND to docs/ARCHITECTURE.md §3"
    )


def test_dependency_law():
    violations = []
    for pkg, allowed in ALLOWED.items():
        pkg_dir = PACKAGE_ROOT / pkg
        if not pkg_dir.exists():
            continue  # future package; law pre-registered
        for module in pkg_dir.rglob("*.py"):
            for target in internal_imports(module):
                if target != pkg and target not in allowed:
                    violations.append(
                        f"{module.relative_to(PACKAGE_ROOT.parent)} imports "
                        f"quantropy.{target} (not allowed from {pkg!r})"
                    )
    assert not violations, "dependency-law violations:\n  " + "\n  ".join(violations)


def test_core_imports_nothing_internal():
    """core is the bottom of the world — belt and braces on the most important rule."""
    for module in (PACKAGE_ROOT / "core").rglob("*.py"):
        assert not internal_imports(module) - {"core"}, f"{module} imports outside core"
