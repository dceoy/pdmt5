# Feature Specification: MT5 client operations

**Feature Branch**: `047-mt5-client-operations`  
**Created**: 2026-02-05  
**Status**: Draft  
**Input**: User description: "MT5 client operations baseline spec"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Connect and verify MT5 session (Priority: P1)

As a trading analyst, I want to initialize and optionally log in to an MT5 terminal, then retrieve terminal/account metadata so I can confirm connectivity before requesting market data.

**Why this priority**: Connectivity and status validation are prerequisites for all MT5 operations.

**Independent Test**: Can be fully tested by initializing the client, logging in, retrieving version/account/terminal info, and shutting down in a single session.

**Acceptance Scenarios**:

1. **Given** valid MT5 credentials, **When** I initialize and login, **Then** the client reports success and logs the MT5 last status code.
2. **Given** an initialized client, **When** I request account or terminal info, **Then** I receive the latest MT5 metadata or a runtime error with last-error context.

---

### User Story 2 - Retrieve market data in tabular form (Priority: P2)

As a data analyst, I want symbols, rates, ticks, and market book data returned as DataFrames or dictionaries so I can analyze market state without manual conversions.

**Why this priority**: Data access in pandas-friendly formats is the primary value of the library for analysis workflows.

**Independent Test**: Can be fully tested by requesting symbols, rates, ticks, and market book data with optional time conversion and index settings.

**Acceptance Scenarios**:

1. **Given** a valid symbol and timeframe, **When** I request rates or ticks, **Then** I receive a DataFrame with time fields converted to datetime unless I opt out.
2. **Given** a symbol group or filter, **When** I request symbols or market depth, **Then** I receive a DataFrame/list representation or an empty result when no data exists.

---

### User Story 3 - Manage trades and trading metrics (Priority: P3)

As a trader, I want to check/send orders, close positions, update SL/TP, and compute margin/spread metrics so I can manage risk and execution decisions programmatically.

**Why this priority**: Trading operations and metrics build on data access and enable real trading workflows.

**Independent Test**: Can be fully tested by sending dry-run order checks and computing margin/position metrics using mocked MT5 responses.

**Acceptance Scenarios**:

1. **Given** open positions, **When** I request a close operation or SL/TP update, **Then** I receive per-position results and warnings for empty sets.
2. **Given** margin and market data, **When** I request trading metrics, **Then** I receive numeric outputs or empty results without unhandled exceptions.

---

### Edge Cases

- What happens when the MT5 terminal is not installed or cannot be initialized?
- How does the client behave when MT5 returns `None` for data operations?
- What happens when invalid counts, date ranges, or negative values are provided?
- How does dry-run mode behave if MT5 rejects validation requests?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST initialize and optionally log in to the MT5 terminal using path, login, password, server, and timeout parameters.
- **FR-002**: System MUST enforce initialization before executing MT5 operations and log the MT5 last status after each call.
- **FR-003**: System MUST surface MT5 failures as runtime errors with contextual details when responses are missing or operations error.
- **FR-004**: System MUST expose terminal, account, symbol, order, position, and history retrieval methods as dictionary or DataFrame outputs.
- **FR-005**: System MUST convert MT5 time fields to datetime by default, with an opt-out toggle per call.
- **FR-006**: System MUST allow callers to set DataFrame indices when data is non-empty and index keys are provided.
- **FR-007**: System MUST validate input ranges for counts, positions, dates, and positive numeric values before executing MT5 operations.
- **FR-008**: System MUST support order checking/sending, position closing, SL/TP updates, and market order placement with dry-run support.
- **FR-009**: System MUST calculate trading metrics including margins, spread ratios, and new position margin ratios.
- **FR-010**: System MUST provide convenience data fetches for latest rates, latest ticks, entry deals, and positions with derived metrics.

### Key Entities _(include if feature involves data)_

- **MT5 Client**: Session wrapper managing initialization, login, MT5 API calls, logging, and error handling.
- **MT5 Data Client**: MT5 client exposing DataFrame/dict outputs with time conversion and validation helpers.
- **Trading Client**: Data client extension that performs trading operations and calculates derived metrics.
- **Connection Config**: Validated credentials and terminal configuration for initialization/login.
- **Trading Request**: Structured order parameters for check/send/close/SLTP operations.
- **Trading Result**: Structured order responses for checks/sends/position updates.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Initialization and login succeed for valid credentials without raising exceptions in tests.
- **SC-002**: Data retrieval helpers return DataFrames with consistent schemas and time columns converted to datetime by default.
- **SC-003**: Trading helper methods return structured results and respect dry-run or raise-on-error toggles in tests.
- **SC-004**: Validation guards prevent invalid input from reaching MT5 API calls and are covered by unit tests.

## Assumptions

- MT5 terminal and broker connectivity exist on the target Windows environment.
- MT5 API returns structured objects that can be converted to dictionaries via `_asdict()`.
- The library operates in a single-threaded context due to MT5 API constraints.
