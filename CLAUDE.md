# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup

```bash
# Install dependencies with uv (modern Python package manager)
uv sync
```

### Code Quality

```bash
# Run all linting and formatting
uv run ruff check --fix .
uv run ruff format .

# Type checking
uv run pyright .
```

### Testing

```bash
# Run unit tests with pytest
uv run pytest test/ -v

# Type checking with pyright
uv run pyright .
```

## Architecture

### Project Overview

- **Purpose**: Pandas-based data handler for MetaTrader 5 trading platform
- **Target Platform**: Windows only (MetaTrader5 API requirement)
- **Domain**: Financial/trading data analysis
- **Status**: Early development (v0.0.1, Beta)

### Key Dependencies

- **MetaTrader5**: Windows-only trading platform API for market data
- **pandas**: Core data manipulation and analysis
- **pydantic**: Data validation and serialization for financial data models

### Package Structure

- `pdmt5/`: Main package directory
- `test/`: Test directory (pytest-based)
- Modern Python packaging with `pyproject.toml`

### Development Tools Configuration

- **Ruff**: Comprehensive linting with 40+ rule categories enabled
- **Pyright**: Strict type checking mode
- **pytest**: Testing with coverage reporting (50% minimum)
- **Google-style docstrings**: Documentation convention
- **Line length**: 88 characters

### Quality Standards

- Type hints required (strict mode)
- Comprehensive linting rules including security (bandit), pandas-specific rules
- Test coverage tracking with branch coverage
- Professional financial software standards

## Development Methodology

This section combines essential guidance from Martin Fowler's refactoring, Kent Beck's tidying, and t_wada's TDD approaches.

### Core Philosophy

- **Small, safe, behavior-preserving changes** - Every change should be tiny, reversible, and testable
- **Separate concerns** - Never mix adding features with refactoring/tidying
- **Test-driven workflow** - Tests provide safety net and drive design
- **Economic justification** - Only refactor/tidy when it makes immediate work easier

### The Development Cycle

1. **Red** - Write a failing test first (TDD)
2. **Green** - Write minimum code to pass the test
3. **Refactor/Tidy** - Clean up without changing behavior
4. **Commit** - Separate commits for features vs refactoring

### Essential Practices

#### Before Coding

- Create TODO list for complex tasks
- Ensure test coverage exists
- Identify code smells (long functions, duplication, etc.)

#### While Coding

- **Test-First**: Write the test before the implementation
- **Small Steps**: Each change should be easily reversible
- **Run Tests Frequently**: After each small change
- **Two Hats**: Either add features OR refactor, never both

#### Refactoring Techniques

1. **Extract Function/Variable** - Improve readability
2. **Rename** - Use meaningful names
3. **Guard Clauses** - Replace nested conditionals
4. **Remove Dead Code** - Delete unused code
5. **Normalize Symmetries** - Make similar code consistent

#### TDD Strategies

1. **Fake It** - Start with hardcoded values
2. **Obvious Implementation** - When solution is clear
3. **Triangulation** - Multiple tests to find general solution

### When to Apply

- **Rule of Three**: Refactor on third duplication
- **Preparatory**: Before adding features to messy code
- **Comprehension**: As you understand code better
- **Opportunistic**: Small improvements during daily work

### Key Reminders

- One assertion per test
- Commit refactoring separately from features
- Delete redundant tests
- Focus on making code understandable to humans

Quote: "Make the change easy, then make the easy change." - Kent Beck
