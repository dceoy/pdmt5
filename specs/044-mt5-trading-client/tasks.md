# Tasks: Mt5 Trading Client

**Feature**: Mt5 Trading Client  
**Branch**: `044-mt5-trading-client`  
**Spec**: `/specs/044-mt5-trading-client/spec.md`  
**Plan**: `/specs/044-mt5-trading-client/plan.md`

## Implementation Strategy

Validate the Mt5TradingClient behavior against the spec by confirming position
management, dry-run order checks, and metrics in pdmt5/trading.py and
corresponding tests.

## Phase 1: Setup

- [x] T001 Review Mt5TradingClient and trading helpers (pdmt5/trading.py)
- [x] T002 Map spec requirements to tests (tests/test_trading.py)

## Phase 2: Foundational

- [x] T003 Validate trading error handling and retcode mapping (pdmt5/trading.py, tests/test_trading.py)
- [x] T004 Validate order request normalization helpers (pdmt5/trading.py, tests/test_trading.py)

## Phase 3: User Story 1 - Close Positions Safely (P1)

**Goal**: Confirm position closing helpers handle symbols and empty results.

**Independent Test**: Mock MT5 positions and validate close requests per symbol.

- [x] T005 [US1] Validate close positions by symbol or all (pdmt5/trading.py, tests/test_trading.py)
- [x] T006 [P] [US1] Validate empty position handling and warnings (pdmt5/trading.py, tests/test_trading.py)

## Phase 4: User Story 2 - Dry Run Trading Validation (P2)

**Goal**: Ensure dry-run mode validates orders without execution.

**Independent Test**: Submit dry-run operations and confirm order_check usage.

- [x] T007 [US2] Validate dry-run order check flow (pdmt5/trading.py, tests/test_trading.py)
- [x] T008 [P] [US2] Validate live order flow when dry_run is false (pdmt5/trading.py, tests/test_trading.py)

## Phase 5: User Story 3 - Compute Trading Metrics (P3)

**Goal**: Confirm metrics helpers return numeric outputs or empty results.

**Independent Test**: Mock MT5 symbol/position data to validate metrics.

- [x] T009 [US3] Validate minimum margin and volume-by-margin helpers (pdmt5/trading.py, tests/test_trading.py)
- [x] T010 [P] [US3] Validate spread ratio and position metrics helpers (pdmt5/trading.py, tests/test_trading.py)

## Phase 6: Polish & Cross-Cutting

- [x] T011 Reconcile docs/spec with current behavior (specs/044-mt5-trading-client/spec.md, README.md)
- [x] T012 Run local QA to ensure coverage remains 100% (local-qa)

## Dependencies

- Requires Mt5DataClient (specs/043-mt5-dataframe-client/spec.md).
- Depends on utils helpers for conversions (specs/045-mt5-utils/spec.md).

## Parallel Execution Examples

- US1: T006 can run in parallel after T005.
- US2: T008 can run in parallel after T007.
- US3: T010 can run in parallel after T009.

## Story Completion Order

1. US1 (Close Positions Safely)
2. US2 (Dry Run Trading Validation)
3. US3 (Compute Trading Metrics)
