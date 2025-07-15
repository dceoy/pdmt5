# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Code Design Principles

Follow Robert C. Martin's SOLID and Clean Code principles:

### SOLID Principles

1. **SRP (Single Responsibility)**: One reason to change per class; separate concerns (e.g., storage vs formatting vs calculation)
2. **OCP (Open/Closed)**: Open for extension, closed for modification; use polymorphism over if/else chains
3. **LSP (Liskov Substitution)**: Subtypes must be substitutable for base types without breaking expectations
4. **ISP (Interface Segregation)**: Many specific interfaces over one general; no forced unused dependencies
5. **DIP (Dependency Inversion)**: Depend on abstractions, not concretions; inject dependencies

### Clean Code Practices

- **Naming**: Intention-revealing, pronounceable, searchable names (`daysSinceLastUpdate` not `d`)
- **Functions**: Small, single-task, verb names, 0-3 args, extract complex logic
- **Classes**: Follow SRP, high cohesion, descriptive names
- **Error Handling**: Exceptions over error codes, no null returns, provide context, try-catch-finally first
- **Testing**: TDD, one assertion/test, FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely), Arrange-Act-Assert pattern
- **Code Organization**: Variables near usage, instance vars at top, public then private functions, conceptual affinity
- **Comments**: Self-documenting code preferred, explain "why" not "what", delete commented code
- **Formatting**: Consistent, vertical separation, 88-char limit, team rules override preferences
- **General**: DRY, KISS, YAGNI, Boy Scout Rule, fail fast

## Development Methodology

Follow Martin Fowler's Refactoring, Kent Beck's Tidy Code, and t_wada's TDD principles:

### Core Philosophy

- **Small, safe changes**: Tiny, reversible, testable modifications
- **Separate concerns**: Never mix features with refactoring
- **Test-driven**: Tests provide safety and drive design
- **Economic**: Only refactor when it aids immediate work

### TDD Cycle

1. **Red** → Write failing test
2. **Green** → Minimum code to pass
3. **Refactor** → Clean without changing behavior
4. **Commit** → Separate commits for features vs refactoring

### Practices

- **Before**: Create TODOs, ensure coverage, identify code smells
- **During**: Test-first, small steps, frequent tests, two hats rule
- **Refactoring**: Extract function/variable, rename, guard clauses, remove dead code, normalize symmetries
- **TDD Strategies**: Fake it, obvious implementation, triangulation

### When to Apply

- Rule of Three (3rd duplication)
- Preparatory (before features)
- Comprehension (as understanding grows)
- Opportunistic (daily improvements)

### Key Rules

- One assertion per test
- Separate refactoring commits
- Delete redundant tests
- Human-readable code first

> "Make the change easy, then make the easy change." - Kent Beck

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

### Documentation

```bash
# Build documentation with MkDocs
uv run mkdocs build

# Serve documentation locally with live reload
uv run mkdocs serve

# Deploy documentation to GitHub Pages
uv run mkdocs gh-deploy
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
  - `__init__.py`: Package initialization and exports
  - `exception.py`: Custom exception handling (`Mt5RuntimeError`)
  - `manipulator.py`: Core data client (`Mt5Config`, `Mt5DataClient`)
  - `printer.py`: Pretty printing and export (`Mt5DataPrinter`)
- `test/`: Test directory (pytest-based)
- `docs/`: MkDocs documentation source files
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

## Documentation with MkDocs

### Overview

The project uses MkDocs with the Material theme for generating API documentation. The documentation is automatically built from docstrings and markdown files.

### Configuration

- **Theme**: Material with dark/light mode toggle
- **Plugin**: mkdocstrings for Python API documentation
- **Docstring Style**: Google-style docstrings
- **Features**: Code highlighting, navigation tabs, search functionality

### Documentation Structure

```
docs/
├── index.md              # Main documentation page
└── api/
    ├── index.md          # API overview
    ├── exception.md      # Exception handling documentation
    ├── manipulator.md    # Core data client documentation
    └── printer.md        # Pretty printing and export documentation
```

### Navigation

The documentation includes:
- **Home**: Project overview and getting started
- **API Reference**: Comprehensive API documentation
  - Overview of all modules
  - Exception handling (`Mt5RuntimeError`)
  - Core data client functionality (`Mt5DataClient`)
  - Pretty printing and export functionality (`Mt5DataPrinter`)

### Development Workflow

1. **Writing Documentation**: Add Google-style docstrings to all functions and classes
2. **Local Testing**: Use `uv run mkdocs serve` for live preview
3. **Building**: Use `uv run mkdocs build` to generate static site
4. **Deployment**: Use `uv run mkdocs gh-deploy` for GitHub Pages

### Docstring Guidelines

- Use Google-style docstrings consistently
- Include type hints in function signatures
- Document all parameters, returns, and exceptions
- Provide usage examples for complex functions

## Web Search Instructions

For tasks requiring web search, always use `gemini` command instead of the built-in web search tool.

### Usage

```sh
# Basic search query
gemini --sandbox --prompt "WebSearch: <query>"

# Example: Search for latest news
gemini --sandbox --prompt "WebSearch: What are the latest developments in AI?"
```

### Policy

When users request information that requires web search:

1. Use `gemini --sandbox --prompt` command via terminal
2. Parse and present the Gemini response appropriately

This ensures consistent and reliable web search results through the Gemini API.
