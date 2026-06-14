# Repository Guidelines

## Project Structure & Module Organization

This is a Python package for pandas-friendly MetaTrader 5 access. Core code
lives in `pdmt5/`: `mt5.py` wraps MT5 calls, `dataframe.py` adds DataFrame/dict
conversions, `trading.py` contains trading helpers, and `constants.py`/`utils.py`
hold shared parsing and utilities. Tests live in `tests/`, documentation in
`docs/`, and project settings in `pyproject.toml`. Keep `uv.lock` in sync.

## Build, Test, and Development Commands

- `uv sync --group dev`: install runtime and development dependencies.
- `.agents/skills/local-qa/scripts/qa.sh`: run the required local QA workflow
  after any file update.
- `uv run pytest`: run tests, doctests, and coverage.
- `uv run ruff check .`: lint all Python files.
- `uv run ruff format .`: format Python files.
- `uv run pyright`: run strict static type checking.
- `uv run mkdocs serve`: preview documentation locally.

MetaTrader5 and live terminal access are Windows-specific; CI runs on Windows.

## Coding Style & Naming Conventions

Target Python 3.11+. Use type hints throughout and keep Pyright strict mode
clean. Ruff enforces 88-character lines, import sorting, Google-style
docstrings, pandas-vet rules, security checks, and bug-prevention rules.
Use `snake_case` for functions, methods, variables, and modules; `PascalCase`
for classes; and uppercase names for constants. Prefer small typed helpers over
duplicated conversion logic, especially around MT5 result normalization.

## Design Principles

Apply KISS, DRY, and YAGNI. Keep changes straightforward, remove duplication
only when it improves clarity, and do not add extension points or features before
they are needed. Prefer small, test-backed changes that are easy to review.

## Testing Guidelines

Tests use `pytest`, `pytest-mock`, doctests, and `pytest-cov`. Name files
`test_*.py`, classes `Test*`, and functions `test_*`. Coverage targets `pdmt5`
with branch coverage and a 100% threshold. Add tests for behavior changes,
including MT5 import failures, validation errors, and DataFrame conversion paths.

## Commit & Pull Request Guidelines

Recent history uses concise imperative subjects, often with PR numbers, such as
`Refactor dataframe and trading helpers to reduce duplication (#65)`. Dependency
automation may use Conventional Commit style, for example `build(deps): ...`.
Keep commits focused.

Pull requests should include a short summary, QA result, and related issues when
applicable. For API or docs changes, update `README.md` or `docs/`. Note any
Windows/MT5 assumptions reviewers need to verify.

## Security & Configuration Tips

Do not commit MT5 account credentials, terminal paths containing secrets, or live
trading configuration. Use `Mt5Config` inputs or environment-specific setup in
local scripts. Preserve dry-run pathways and mock-based tests when modifying
trading behavior.
