# Tasks: Mt5 Core Client

**Feature**: Mt5 Core Client  
**Branch**: `042-mt5-core-client`  
**Spec**: `/specs/042-mt5-core-client/spec.md`  
**Plan**: `/specs/042-mt5-core-client/plan.md`

## Implementation Strategy

Validate the existing MT5 core client behaviors against the specification. Focus
on lifecycle management, core data retrieval, and error handling coverage within
pdmt5/mt5.py and related tests.

## Phase 1: Setup

- [x] T001 Review current module layout for Mt5Client and MT5 helpers (pdmt5/mt5.py)
- [x] T002 Map spec requirements to existing tests (tests/test_mt5.py)

## Phase 2: Foundational

- [x] T003 Validate initialization/login lifecycle and context manager behavior (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T004 Validate logging and runtime error propagation with last_error context (pdmt5/mt5.py, tests/test_mt5.py)

## Phase 3: User Story 1 - Connect and Manage MT5 Session (P1)

**Goal**: Confirm session lifecycle and initialization safeguards.

**Independent Test**: Mock MT5 initialize/shutdown and confirm context manager
ensures cleanup after errors.

- [x] T005 [US1] Verify context manager initializes and shuts down MT5 (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T006 [P] [US1] Verify MT5 calls raise Mt5RuntimeError when uninitialized (pdmt5/mt5.py, tests/test_mt5.py)

## Phase 4: User Story 2 - Access Core MT5 Data (P2)

**Goal**: Validate account, terminal, symbol, tick, and rate retrieval helpers.

**Independent Test**: Mock MT5 data responses to verify dict outputs and empty
result handling.

- [x] T007 [US2] Validate account and terminal info helpers (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T008 [P] [US2] Validate symbol and tick retrieval helpers (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T009 [P] [US2] Validate rate and market book retrieval helpers (pdmt5/mt5.py, tests/test_mt5.py)

## Phase 5: User Story 3 - Access Trading and History Operations (P3)

**Goal**: Validate orders, positions, and history retrieval APIs.

**Independent Test**: Mock MT5 order/position/history responses to confirm
structures and empty result behavior.

- [x] T010 [US3] Validate orders and positions retrieval (pdmt5/mt5.py, tests/test_mt5.py)
- [x] T011 [P] [US3] Validate history orders and deals retrieval (pdmt5/mt5.py, tests/test_mt5.py)

## Phase 6: Polish & Cross-Cutting

- [x] T012 Reconcile docs/spec with current behavior (specs/042-mt5-core-client/spec.md, README.md)
- [x] T013 Run local QA to ensure coverage remains 100% (local-qa)

## Dependencies

- US1 must be validated before US2 and US3.
- US2 data helpers should be verified before US3 history helpers.

## Parallel Execution Examples

- US1: T006 can run in parallel after T005.
- US2: T008 and T009 can run in parallel after T007.
- US3: T011 can run in parallel after T010.

## Story Completion Order

1. US1 (Connect and Manage MT5 Session)
2. US2 (Access Core MT5 Data)
3. US3 (Access Trading and History Operations)
