# Research: MT5 client operations

## Decisions

### Language and runtime

- **Decision**: Keep Python 3.11+ as the runtime requirement.
- **Rationale**: The package enforces >=3.11,<3.14 in pyproject.toml and relies
  on modern typing features.
- **Alternatives considered**: None (existing codebase constraint).

### Dependencies

- **Decision**: Maintain MetaTrader5, pandas, and pydantic as primary
  dependencies.
- **Rationale**: MetaTrader5 provides the trading API, pandas supplies
  DataFrame-based outputs, and pydantic validates configuration.
- **Alternatives considered**: None (core library purpose).

### Platform scope

- **Decision**: Target Windows only.
- **Rationale**: MetaTrader5 is Windows-only and enforced by dependency markers.
- **Alternatives considered**: None (platform dependency).

### Testing strategy

- **Decision**: Continue using pytest with pytest-mock and pytest-cov.
- **Rationale**: Current tests rely on mocking MT5 and require coverage gates.
- **Alternatives considered**: None (existing test suite).
