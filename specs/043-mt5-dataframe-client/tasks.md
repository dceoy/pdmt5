# Tasks: Mt5 DataFrame Client

**Feature**: Mt5 DataFrame Client  
**Branch**: `043-mt5-dataframe-client`  
**Spec**: `/specs/043-mt5-dataframe-client/spec.md`  
**Plan**: `/specs/043-mt5-dataframe-client/plan.md`

## Implementation Strategy

Validate the Mt5DataClient behavior and configuration validation against the
specification. Confirm DataFrame conversions, empty results, and input
validation in pdmt5/dataframe.py and tests/test_dataframe.py.

## Phase 1: Setup

- [x] T001 Review Mt5DataClient and Mt5Config definitions (pdmt5/dataframe.py)
- [x] T002 Map spec requirements to existing tests (tests/test_dataframe.py)

## Phase 2: Foundational

- [x] T003 Validate Mt5Config validation logic and defaults (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T004 Validate conversion helpers for dict/list responses (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 3: User Story 1 - Retrieve MT5 Data as DataFrames (P1)

**Goal**: Confirm DataFrame outputs and time conversions for MT5 data.

**Independent Test**: Mock MT5 responses to validate DataFrame schema and
converted datetime columns.

- [x] T005 [US1] Validate rates/ticks DataFrame helpers and datetime conversion (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T006 [P] [US1] Validate account/symbol DataFrame helpers (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 4: User Story 2 - Use Validated Connection Configuration (P2)

**Goal**: Confirm configuration validation and reuse in Mt5DataClient.

**Independent Test**: Create Mt5Config with valid/invalid inputs and verify
errors or successful client initialization.

- [x] T007 [US2] Validate Mt5Config validation errors and defaults (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T008 [P] [US2] Validate Mt5DataClient uses config for login/init (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 5: User Story 3 - Consistent Empty Results and Input Validation (P3)

**Goal**: Ensure empty results and validation guards are consistent.

**Independent Test**: Request empty ranges and invalid inputs to confirm empty
DataFrames or validation errors.

- [x] T009 [US3] Validate empty DataFrame outputs for empty MT5 responses (pdmt5/dataframe.py, tests/test_dataframe.py)
- [x] T010 [P] [US3] Validate input range/count checks (pdmt5/dataframe.py, tests/test_dataframe.py)

## Phase 6: Polish & Cross-Cutting

- [x] T011 Reconcile docs/spec with current behavior (specs/043-mt5-dataframe-client/spec.md, README.md)
- [x] T012 Run local QA to ensure coverage remains 100% (local-qa)

## Dependencies

- Requires baseline MT5 client (specs/042-mt5-core-client/spec.md).
- Depends on utils helpers for datetime/index conversions (specs/045-mt5-utils/spec.md).

## Parallel Execution Examples

- US1: T006 can run in parallel after T005.
- US2: T008 can run in parallel after T007.
- US3: T010 can run in parallel after T009.

## Story Completion Order

1. US1 (Retrieve MT5 Data as DataFrames)
2. US2 (Use Validated Connection Configuration)
3. US3 (Consistent Empty Results and Input Validation)
