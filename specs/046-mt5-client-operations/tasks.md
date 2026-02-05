# Tasks: MT5 client operations

**Feature**: MT5 client operations  
**Branch**: `046-mt5-client-operations`  
**Spec**: `/specs/046-mt5-client-operations/spec.md`  
**Plan**: `/specs/046-mt5-client-operations/plan.md`

## Implementation Strategy

Start with connectivity primitives (Mt5Client + config) to satisfy User Story 1.
Layer data access helpers (Mt5DataClient) for User Story 2. Finish with trading
helpers and derived metrics for User Story 3. Since this is a baseline spec for
existing code, the tasks focus on verifying code coverage and documentation
alignment rather than new implementation.

## Phase 1: Setup

- [x] T001 Review existing pdmt5 module structure in pdmt5/ and tests/ to map tasks to files (pdmt5/_.py, tests/_.py)
- [x] T002 Confirm spec, plan, and quickstart alignment with README.md (README.md)

## Phase 2: Foundational

- [x] T003 Validate MT5 client initialization, logging, and error handling coverage in pdmt5/mt5.py (pdmt5/mt5.py)
- [x] T004 Validate utility decorators for time conversion and index setting in pdmt5/utils.py (pdmt5/utils.py)

## Phase 3: User Story 1 - Connect and access terminal data (P1)

**Goal**: Validate client initialization/login and terminal/account retrieval APIs.

**Independent Test**: Use mocked MT5 module to verify initialization/login,
version, account_info, and terminal_info behaviors.

- [x] T005 [US1] Verify initialize/login flows and retry behavior align with spec (pdmt5/mt5.py, pdmt5/dataframe.py, tests/test_mt5.py, tests/test_dataframe.py)
- [x] T006 [P] [US1] Confirm version/account/terminal helpers return dict/DF outputs (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T007 [P] [US1] Confirm MT5 last_error logging and runtime error propagation (pdmt5/mt5.py, tests/test_mt5.py)

## Phase 4: User Story 2 - Retrieve market data in data frames (P2)

**Goal**: Validate symbol, rates, ticks, and market book DataFrame/dict helpers.

**Independent Test**: Mock MT5 responses to validate DataFrame outputs and
optional time conversion/indexing.

- [x] T008 [US2] Validate symbols and symbol info helpers (pdmt5/mt5.py, pdmt5/dataframe.py, tests/test_mt5.py, tests/test_dataframe.py)
- [x] T009 [P] [US2] Validate rates and ticks DataFrame helpers and input validation (pdmt5/mt5.py, pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T010 [P] [US2] Validate market book data helpers and DataFrame conversion (pdmt5/mt5.py, pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 5: User Story 3 - Manage orders, positions, and trading metrics (P3)

**Goal**: Validate order/position helpers and trading metrics in Mt5TradingClient.

**Independent Test**: Mock MT5 order and position responses, validate dry-run
behavior and metric calculations.

- [x] T011 [US3] Validate order check/send helpers and result flattening (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T012 [P] [US3] Validate orders/positions/history helpers with filters (pdmt5/mt5.py, pdmt5/dataframe.py, tests/test_mt5.py, tests/test_dataframe.py)
- [x] T013 [P] [US3] Validate trading operations and metrics calculations (pdmt5/trading.py, tests/test_trading.py)

## Phase 6: Polish & Cross-Cutting

- [x] T014 Reconcile docs/spec with any identified gaps (specs/046-mt5-client-operations/spec.md, README.md, docs/index.md)
- [x] T015 Run local QA to ensure coverage remains 100% (local-qa)

## Dependencies

- US1 must be validated before US2 and US3.
- US2 data access coverage should precede US3 trading helpers.

## Parallel Execution Examples

- US1: T006 and T007 can run in parallel after T005.
- US2: T009 and T010 can run in parallel after T008.
- US3: T012 and T013 can run in parallel after T011.

## Story Completion Order

1. US1 (Connect and access terminal data)
2. US2 (Retrieve market data in data frames)
3. US3 (Manage orders, positions, and trading metrics)
