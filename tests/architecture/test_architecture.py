"""Contract tests that keep pdmt5 at the low-level MT5 boundary."""

from __future__ import annotations

import ast
from pathlib import Path

from pdmt5 import constants, dataframe, mt5, utils

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_ROOT = _REPOSITORY_ROOT / "pdmt5"
_TESTS_ROOT = _REPOSITORY_ROOT / "tests"
_FORBIDDEN_DOWNSTREAM_PACKAGES = {"mt5cli", "mteor"}
_OUT_OF_BAND_TEST_DIRECTORIES = ("architecture", "contracts")


def _imported_root_names(module_path: Path) -> set[str]:
    """Return absolute top-level packages imported by one production module."""
    module = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_names: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported_names.add(node.module.split(".")[0])
    return imported_names


def _eligible_production_modules() -> set[str]:
    """Return eligible top-level production module names."""
    return {
        path.stem for path in _PACKAGE_ROOT.glob("*.py") if path.name != "__init__.py"
    }


def _strict_unit_tests_by_module() -> dict[str, list[Path]]:
    """Return direct root unit-test paths grouped by mapped module name."""
    unit_tests: dict[str, list[Path]] = {}
    for path in _TESTS_ROOT.glob("test_*.py"):
        module_name = path.stem.removeprefix("test_")
        unit_tests.setdefault(module_name, []).append(path)
    return unit_tests


def _out_of_band_test_paths() -> set[Path]:
    """Return architecture and contract tests outside the strict unit scope."""
    return {
        path
        for directory in _OUT_OF_BAND_TEST_DIRECTORIES
        for path in (_TESTS_ROOT / directory).glob("test_*.py")
    }


def test_module_public_apis_match_contract() -> None:
    """Test that every production module has a deliberate public API."""
    assert mt5.__all__ == ["Mt5Client", "Mt5RuntimeError"]
    assert dataframe.__all__ == ["Mt5Config", "Mt5DataClient"]
    assert constants.__all__ == [
        "COPY_TICKS_MAP",
        "ORDER_TYPE_MAP",
        "TIMEFRAME_MAP",
        "get_copy_ticks_name",
        "get_copy_ticks_value",
        "get_order_type_name",
        "get_order_type_value",
        "get_timeframe_name",
        "get_timeframe_value",
        "list_copy_ticks_names",
        "list_copy_ticks_values",
        "list_order_type_names",
        "list_order_type_values",
        "list_timeframe_names",
        "list_timeframe_values",
        "parse_copy_ticks",
        "parse_order_type",
        "parse_timeframe",
    ]
    assert utils.__all__ == []


def test_production_modules_do_not_import_downstream_packages() -> None:
    """Test the dependency direction never points from pdmt5 downstream."""
    for module_path in _PACKAGE_ROOT.rglob("*.py"):
        imported_names = _imported_root_names(module_path)
        forbidden_imports = imported_names & _FORBIDDEN_DOWNSTREAM_PACKAGES
        assert not forbidden_imports, (
            f"{module_path} imports forbidden downstream package(s):"
            f" {sorted(forbidden_imports)}"
        )


def test_nested_module_importing_downstream_package_is_detected(
    tmp_path: Path,
) -> None:
    """Test that the recursive scan reaches modules under nested subpackages."""
    nested_module = tmp_path / "execution" / "workflow.py"
    nested_module.parent.mkdir(parents=True)
    nested_module.write_text("import mt5cli\n", encoding="utf-8")

    imported_names = _imported_root_names(nested_module)

    assert imported_names & _FORBIDDEN_DOWNSTREAM_PACKAGES == {"mt5cli"}
    assert list(tmp_path.rglob("*.py")) == [nested_module]


def test_production_and_unit_test_modules_have_one_to_one_mapping() -> None:
    """Test that direct production and unit-test modules map exactly once."""
    production_modules = _eligible_production_modules()
    unit_tests = _strict_unit_tests_by_module()

    assert set(unit_tests) == production_modules
    for module_name, paths in unit_tests.items():
        assert paths == [_TESTS_ROOT / f"test_{module_name}.py"]


def test_architecture_and_contract_tests_stay_outside_unit_mapping() -> None:
    """Test that scoped tests are not counted as strict unit-test modules."""
    strict_unit_tests = {
        path for paths in _strict_unit_tests_by_module().values() for path in paths
    }
    out_of_band_tests = _out_of_band_test_paths()

    assert out_of_band_tests
    assert strict_unit_tests.isdisjoint(out_of_band_tests)
    assert all(path.parent != _TESTS_ROOT for path in out_of_band_tests)
