# Tasks: MT5 client operations

**Feature**: MT5 client operations  
**Branch**: `047-mt5-client-operations`  
**Spec**: `/specs/047-mt5-client-operations/spec.md`  
**Plan**: `/specs/047-mt5-client-operations/plan.md`

## Implementation Strategy

Validate the MT5 client operations baseline against current pdmt5 behavior.
Focus on connectivity, data access, trading helpers, validation guards, and
metrics derived from existing implementation.

## Phase 1: Setup

- [x] T001 Review MT5 client modules and tests (pdmt5/mt5.py, pdmt5/dataframe.py, pdmt5/trading.py, tests/test\_\*.py)
- [x] T002 Map spec requirements to existing behaviors and docs (specs/047-mt5-client-operations/spec.md)

## Phase 2: Foundational

- [x] T003 Validate initialization/login and last-error logging (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T004 Validate input validation helpers for counts, dates, and numeric values (pdmt5/utils.py, tests/test_utils.py)

## Phase 3: User Story 1 - Connect and verify MT5 session (P1)

**Goal**: Confirm connectivity, login, and status retrieval behaviors.

**Independent Test**: Mock MT5 initialize/login/version/account/terminal calls in
one session and confirm runtime error handling.

- [x] T005 [US1] Validate initialize/login flows and MT5 status logging (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T006 [P] [US1] Validate version/account/terminal helpers (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 4: User Story 2 - Retrieve market data in tabular form (P2)

**Goal**: Confirm DataFrame/dict outputs for symbols, rates, ticks, and market book.

**Independent Test**: Mock MT5 responses and verify DataFrame outputs, time
conversion, and indexing.

- [x] T007 [US2] Validate symbol and market book helpers (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T008 [P] [US2] Validate rates/ticks helpers with time conversion and indexing (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T009 [P] [US2] Validate empty result handling for data retrieval (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 5: User Story 3 - Manage trades and trading metrics (P3)

**Goal**: Confirm trading helpers, dry-run behavior, and derived metrics.

**Independent Test**: Mock MT5 order/position/tick responses and verify metrics.

- [x] T010 [US3] Validate order check/send and close operations (pdmt5/trading.py, tests/test_trading.py)
- [x] T011 [P] [US3] Validate SL/TP updates and dry-run behavior (pdmt5/trading.py, tests/test_trading.py)
- [x] T012 [P] [US3] Validate margin/spread/position metrics outputs (pdmt5/trading.py, tests/test_trading.py)

## Phase 6: Polish & Cross-Cutting

- [x] T013 Reconcile docs/spec with current behavior (specs/047-mt5-client-operations/spec.md, README.md)
- [x] T014 Run local QA to ensure coverage remains 100% (local-qa)

## Dependencies

- Requires core client, DataFrame client, and utils baselines (specs/042-045).

## Parallel Execution Examples

- US1: T006 can run in parallel after T005.
- US2: T008 and T009 can run in parallel after T007.
- US3: T011 and T012 can run in parallel after T010.

## Story Completion Order

1. US1 (Connect and verify MT5 session)
2. US2 (Retrieve market data in tabular form)
3. US3 (Manage trades and trading metrics)
