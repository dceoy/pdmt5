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

## Code Design Principles

Follow Robert C. Martin's SOLID and Clean Code principles for maintainable, professional software.

### SOLID Principles

#### 1. Single Responsibility Principle (SRP)
- Each class should have only one reason to change
- Classes should have a single, well-defined responsibility
- Keep classes small and focused
- Example: Separate data storage, formatting, and calculation logic into different classes

#### 2. Open/Closed Principle (OCP)
- Classes should be open for extension but closed for modification
- Add new functionality through extension, not by changing existing code
- Use interfaces and inheritance to enable extensibility
- Example: Use polymorphism instead of if/else chains for handling different types

#### 3. Liskov Substitution Principle (LSP)
- Subtypes must be substitutable for their base types
- Subclasses should not break the behavior expected from the parent class
- Avoid violating expectations when overriding methods

#### 4. Interface Segregation Principle (ISP)
- Clients should not be forced to depend on interfaces they don't use
- Prefer many specific interfaces over one general-purpose interface
- Split large interfaces into smaller, focused ones

#### 5. Dependency Inversion Principle (DIP)
- High-level modules should not depend on low-level modules
- Both should depend on abstractions (interfaces)
- Inject dependencies rather than creating them directly

### Clean Code Practices

#### Naming
- Use intention-revealing names that clearly communicate purpose
- Avoid disinformation and ambiguous terms
- Make meaningful distinctions between similar concepts
- Use pronounceable and searchable names
- Example: `daysSinceLastUpdate` instead of `d`

#### Functions
- Keep functions small and focused on a single task
- Functions should do one thing and do it well
- Use descriptive verb or verb-phrase names
- Limit function arguments (ideally 0-3)
- Extract complex logic into well-named helper functions

#### Classes
- Follow the Single Responsibility Principle
- Maintain high cohesion within classes
- Class names should clearly describe their responsibilities

#### Error Handling
- Use exceptions instead of error codes
- Write try-catch-finally statements first
- Don't return null - throw exceptions or use special case objects
- Provide context with exceptions
- Define exception classes in terms of a caller's needs

#### Testing
- Write tests first (Test-Driven Development)
- One assertion per test for clarity
- Keep tests Fast, Independent, Repeatable, Self-validating, and Timely (FIRST)
- Use the Arrange-Act-Assert pattern
- Test names should clearly describe what is being tested

#### Code Organization
- Variables should be declared close to their usage
- Instance variables at the top of the class
- Public functions should follow the list of variables
- Private utilities should be below the public functions they support
- Maintain conceptual affinity - keep related functions close

#### Comments
- Strive for self-documenting code that doesn't need comments
- Use comments to explain "why" not "what"
- Avoid redundant comments
- Don't comment out code - delete it (version control preserves history)
- Keep comments up-to-date with code changes

#### Formatting
- Maintain consistent formatting throughout the codebase
- Use vertical formatting to separate concepts
- Keep lines short (follow the 88-character limit)
- Use horizontal alignment sparingly
- Team rules override personal preferences

#### General Principles
- Don't Repeat Yourself (DRY) - avoid code duplication
- Keep it Simple (KISS) - favor simple solutions
- You Aren't Gonna Need It (YAGNI) - don't add functionality until needed
- Boy Scout Rule - leave the code cleaner than you found it
- Fail fast - detect and report errors as early as possible
