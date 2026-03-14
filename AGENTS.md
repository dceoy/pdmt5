# Repository Guidelines

## Commands

### Development Setup

```bash
uv sync
```

### Code Quality and Documentation

1. **format, lint, and test**: Use the `local-qa` skill.
2. **Documentation build** (if any public API changes): `uv run mkdocs build`

## Architecture

### Key Dependencies

- **MetaTrader5**: Windows-only trading platform API for market data
- **pandas**: Core data manipulation and analysis
- **pydantic**: Data validation and serialization for financial data models

### Package Structure

- `pdmt5/`: Main package directory
  - `__init__.py`: Package initialization and exports (`Mt5Client`, `Mt5Config`, `Mt5DataClient`, `Mt5RuntimeError`, `Mt5TradingClient`)
  - `mt5.py`: MT5 terminal client with context manager support (`Mt5Client`, `Mt5RuntimeError`)
  - `dataframe.py`: MT5 data client with pandas DataFrame conversion (`Mt5Config`, `Mt5DataClient`)
  - `trading.py`: Trading operations client (`Mt5TradingClient`, `Mt5TradingError`)
  - `utils.py`: Utility decorators and functions for time conversion and DataFrame indexing
- `tests/`: Comprehensive test suite (pytest-based)
  - `test_init.py`, `test_mt5.py`, `test_dataframe.py`, `test_trading.py`, `test_utils.py`
- `docs/`: MkDocs documentation with API reference
  - `docs/index.md`: Main documentation
  - `docs/api/`: Auto-generated API documentation for all modules
- Modern Python packaging with `pyproject.toml` and uv dependency management

### Quality Standards

- Type hints required (pyright strict mode)
- Comprehensive linting with 35+ rule categories (ruff)
- Test coverage tracking with 100% (pytest-cov)
- Parametrized tests for input/result matrices using `pytest.mark.parametrize` (pytest)
- Professional financial software standards
- Pydantic models for data validation and configuration
- Context manager support for resource management

### Documentation workflow

1. Add Google-style docstrings to functions/classes
2. Local preview: `uv run mkdocs serve`
3. Build: `uv run mkdocs build`
4. Deploy: `uv run mkdocs gh-deploy`

## Commit & Pull Request Guidelines

- Run QA checks using `local-qa` skill before committing or creating a PR.
- Branch names use appropriate prefixes on creation (e.g., `feature/...`, `bugfix/...`, `refactor/...`, `docs/...`, `chore/...`).
- When instructed to create a PR, create it as a draft with appropriate labels by default.

## Code Design Principles

Always prefer the simplest design that works.

- **KISS**: Choose straightforward solutions and avoid unnecessary abstraction.
- **DRY**: Remove duplication when it improves clarity and maintainability.
- **YAGNI**: Do not add features, hooks, or flexibility until they are needed.
- **SOLID/Clean Code**: Apply these as tools, only when they keep the design simpler and easier to change.

## Development Methodology

Keep delivery incremental, test-backed, and easy to review.

- Make small, safe, reversible changes.
- Prefer `Red -> Green -> Refactor`.
- Do not mix feature work and refactoring in the same commit.
- Refactor when it improves clarity or removes real duplication (Rule of Three).
- Keep tests fast, focused, and self-validating.
