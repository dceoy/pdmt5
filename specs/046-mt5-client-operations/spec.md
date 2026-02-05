# Feature Specification: MT5 client operations

**Feature Branch**: `046-mt5-client-operations`  
**Created**: 2026-02-05  
**Status**: Draft  
**Input**: User description: "Baseline spec from current pdmt5 package"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Connect and access terminal data (Priority: P1)

As a trading analyst, I can initialize an MT5 session, log in, and retrieve
account/terminal information so that I can validate connectivity before
requesting market data.

**Why this priority**: Connectivity is required for any downstream data or
trading operations.

**Independent Test**: Initialize the client, fetch version/account/terminal
information, and verify non-empty responses.

**Acceptance Scenarios**:

1. **Given** valid terminal credentials, **When** I initialize and login, **Then**
   the client reports success and logs the MT5 status code.
2. **Given** an initialized client, **When** I request account or terminal info,
   **Then** the system returns the current details or raises a runtime error if
   the MT5 response is missing.

---

### User Story 2 - Retrieve market data in data frames (Priority: P2)

As a data analyst, I can fetch symbols, rates, ticks, and market book entries as
pandas DataFrames so that I can analyze time series data efficiently.

**Why this priority**: Data extraction is the primary use case for analysis
workflows.

**Independent Test**: Fetch symbols and rates as data frames with optional index
settings and time conversion.

**Acceptance Scenarios**:

1. **Given** a valid symbol and timeframe, **When** I request rates as a data
   frame, **Then** I receive a DataFrame with expected columns and optional time
   conversion.
2. **Given** a symbol filter or group filter, **When** I request symbols or
   market book data, **Then** I receive a DataFrame representation of the
   underlying MT5 structures.

---

### User Story 3 - Manage orders, positions, and trading metrics (Priority: P3)

As a trader, I can inspect orders/positions, place and check orders, and compute
trading metrics so that I can manage open exposure and evaluate risk.

**Why this priority**: Trading actions build upon data access and require
reliable operational tooling.

**Independent Test**: Submit a market order request (dry run) and compute margin
or spread metrics using mocked MT5 responses.

**Acceptance Scenarios**:

1. **Given** open positions, **When** I request position data or close them, **Then**
   the system returns per-position results and logs failures when they occur.
2. **Given** order request parameters, **When** I check or send the order, **Then**
   the system returns structured results and raises errors when configured to do
   so.

---

### Edge Cases

- What happens when MT5 returns `None` for an operation? The system raises
  runtime errors with last-error context.
- How does the system handle invalid date ranges or counts? The system raises
  validation errors before calling MT5 APIs.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST initialize and optionally log into the MT5 terminal
  using provided path, login, password, server, and timeout.
- **FR-002**: System MUST enforce initialization before executing MT5 operations
  and log the MT5 last status after each call.
- **FR-003**: System MUST surface MT5 failures as runtime errors with contextual
  details when responses are missing or operations error.
- **FR-004**: System MUST expose MT5 terminal, account, symbol, order, position,
  and history retrieval methods as dictionary or DataFrame outputs.
- **FR-005**: System MUST convert MT5 time fields to pandas datetimes unless the
  caller opts out.
- **FR-006**: System MUST allow callers to set DataFrame indices when data is
  non-empty and an index is provided.
- **FR-007**: System MUST validate input ranges (counts, positions, dates, and
  positive numeric values) before executing MT5 data or trading calls.
- **FR-008**: System MUST support order checking/sending, position closing, SL/TP
  updates, and market order placement with dry-run support.
- **FR-009**: System MUST calculate trading metrics including margins, spread
  ratio, and new position margin ratios.
- **FR-010**: System MUST provide convenience data fetches for latest rates,
  latest ticks, entry deals, and positions with derived metrics.

### Key Entities _(include if feature involves data)_

- **MT5 Client**: Session wrapper that manages initialization, login, and
  forwarding of MT5 API calls with logging and error handling.
- **MT5 Data Client**: MT5 client that exposes DataFrame- and dict-based data
  access with time conversion and validation.
- **Trading Client**: Data client extension that performs trading operations and
  calculates derived metrics for positions and margin.
- **Connection Config**: Credentials and terminal configuration used for MT5
  initialization and login.
- **Trading Request**: Structured order request parameters for check/send
  operations.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Initialization and login succeed for valid credentials without
  raising exceptions in unit tests.
- **SC-002**: Data retrieval helpers return DataFrames with consistent schemas
  and time columns converted to datetime in tests.
- **SC-003**: Trading helper methods return structured results and respect dry
  run or raise-on-error toggles in tests.
- **SC-004**: Validation guards prevent invalid input from reaching MT5 API calls
  and are covered by unit tests.
