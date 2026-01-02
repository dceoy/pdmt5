# Tasks: REST API for MetaTrader 5 Data Access

**Input**: Design documents from `/specs/041-mt5-rest-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included as per project CLAUDE.md requirements (TDD mandatory, 100% coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `pdmt5/` (library), `tests/` at repository root, `docs/` for documentation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create API package structure in pdmt5/api/ directory
- [X] T002 Update pyproject.toml with api extras dependencies (FastAPI, uvicorn, pyarrow, etc.)
- [X] T003 [P] Create test structure in tests/test_api/ directory
- [X] T004 [P] Update README.md with API installation and usage section

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create FastAPI application instance in pdmt5/api/main.py with lifespan management
- [ ] T006 [P] Implement Mt5DataClient singleton dependency in pdmt5/api/dependencies.py
- [ ] T007 [P] Create base Pydantic models (ResponseFormat enum, ErrorResponse) in pdmt5/api/models.py
- [ ] T008 Implement error handling middleware in pdmt5/api/middleware.py
- [ ] T009 [P] Create format negotiation dependency in pdmt5/api/dependencies.py
- [ ] T010 [P] Implement JSON formatter in pdmt5/api/formatters.py
- [ ] T011 [P] Implement Parquet formatter in pdmt5/api/formatters.py
- [ ] T012 [P] Create async MT5 wrapper using asyncio.to_thread() in pdmt5/api/dependencies.py
- [ ] T013 Create pytest fixtures for test client and mocked MT5Client in tests/test_api/conftest.py
- [ ] T014 Create health router in pdmt5/api/routers/health.py with /health endpoint
- [ ] T015 Write tests for health endpoint in tests/test_api/test_health.py
- [ ] T016 [P] Implement API key authentication in pdmt5/api/auth.py
- [ ] T017 [P] Write tests for authentication in tests/test_api/test_auth.py
- [ ] T018 Write tests for format negotiation in tests/test_api/test_formatters.py
- [ ] T019 Run quality checks (ruff format, ruff check, pyright, pytest)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Market Data Retrieval via HTTP (Priority: P1) 🎯 MVP

**Goal**: Enable retrieval of current market data (symbols, ticks, and rates) through HTTP requests

**Independent Test**: Make GET requests to symbol and market data endpoints and verify correct JSON/Parquet responses

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (TDD)**

- [ ] T020 [P] [US1] Write contract tests for symbols endpoints in tests/test_api/test_symbols.py
- [ ] T021 [P] [US1] Write contract tests for market data endpoints in tests/test_api/test_market.py
- [ ] T022 [P] [US1] Write integration tests for symbol retrieval journey in tests/test_api/test_integration.py

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create request models (SymbolsRequest, SymbolInfoRequest, SymbolTickRequest) in pdmt5/api/models.py
- [ ] T024 [P] [US1] Create request models (RatesFromRequest, RatesFromPosRequest, RatesRangeRequest) in pdmt5/api/models.py
- [ ] T025 [P] [US1] Create request models (TicksFromRequest, TicksRangeRequest, MarketBookRequest) in pdmt5/api/models.py
- [ ] T026 [US1] Implement symbols router with GET /api/v1/symbols endpoint in pdmt5/api/routers/symbols.py
- [ ] T027 [US1] Implement GET /api/v1/symbols/{symbol} endpoint in pdmt5/api/routers/symbols.py
- [ ] T028 [US1] Implement GET /api/v1/symbols/{symbol}/tick endpoint in pdmt5/api/routers/symbols.py
- [ ] T029 [US1] Implement market router with GET /api/v1/rates/from endpoint in pdmt5/api/routers/market.py
- [ ] T030 [US1] Implement GET /api/v1/rates/from-pos endpoint in pdmt5/api/routers/market.py
- [ ] T031 [US1] Implement GET /api/v1/rates/range endpoint in pdmt5/api/routers/market.py
- [ ] T032 [US1] Implement GET /api/v1/ticks/from endpoint in pdmt5/api/routers/market.py
- [ ] T033 [US1] Implement GET /api/v1/ticks/range endpoint in pdmt5/api/routers/market.py
- [ ] T034 [US1] Implement GET /api/v1/market-book/{symbol} endpoint in pdmt5/api/routers/market.py
- [ ] T035 [US1] Register symbols and market routers in pdmt5/api/main.py
- [ ] T036 [US1] Run tests and verify all US1 endpoints work with both JSON and Parquet formats
- [ ] T037 [US1] Run quality checks (ruff format, ruff check, pyright, pytest)

**Checkpoint**: At this point, User Story 1 should be fully functional - clients can retrieve market data via HTTP

---

## Phase 4: User Story 2 - Account and Terminal Information Access (Priority: P2)

**Goal**: Enable monitoring of MT5 terminal status and account information through the API

**Independent Test**: Request account info, terminal status, and version information endpoints without any trading activity

### Tests for User Story 2

- [ ] T038 [P] [US2] Write contract tests for account endpoint in tests/test_api/test_account.py
- [ ] T039 [P] [US2] Write integration tests for account monitoring in tests/test_api/test_integration.py

### Implementation for User Story 2

- [ ] T040 [P] [US2] Create request models (AccountInfoRequest, TerminalInfoRequest) in pdmt5/api/models.py
- [ ] T041 [US2] Implement account router with GET /api/v1/account endpoint in pdmt5/api/routers/account.py
- [ ] T042 [US2] Implement GET /api/v1/terminal endpoint in pdmt5/api/routers/account.py
- [ ] T043 [US2] Implement GET /api/v1/version endpoint in pdmt5/api/routers/account.py
- [ ] T044 [US2] Register account router in pdmt5/api/main.py
- [ ] T045 [US2] Run tests and verify all US2 endpoints work with both formats
- [ ] T046 [US2] Run quality checks (ruff format, ruff check, pyright, pytest)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 4 - Historical Trading Data Access (Priority: P4)

**Goal**: Enable retrieval of historical order and deal information for backtesting and analysis

**Independent Test**: Query historical orders and deals endpoints with date ranges and verify complete transaction history

### Tests for User Story 4

- [ ] T047 [P] [US4] Write contract tests for history endpoints in tests/test_api/test_history.py
- [ ] T048 [P] [US4] Write integration tests for historical data retrieval in tests/test_api/test_integration.py

### Implementation for User Story 4

- [ ] T049 [P] [US4] Create request models (HistoryOrdersRequest, HistoryDealsRequest) in pdmt5/api/models.py
- [ ] T050 [US4] Implement history router with GET /api/v1/history/orders endpoint in pdmt5/api/routers/history.py
- [ ] T051 [US4] Implement GET /api/v1/history/deals endpoint in pdmt5/api/routers/history.py
- [ ] T052 [US4] Add request validation for date range or ticket/position requirement in pdmt5/api/models.py
- [ ] T053 [US4] Register history router in pdmt5/api/main.py
- [ ] T054 [US4] Run tests and verify all US4 endpoints work with both formats
- [ ] T055 [US4] Run quality checks (ruff format, ruff check, pyright, pytest)

**Checkpoint**: Historical data retrieval should be functional independently

---

## Phase 6: User Story 5 - Active Positions and Orders Monitoring (Priority: P5)

**Goal**: Enable retrieval of current open positions and pending orders for external monitoring

**Independent Test**: Place orders/positions in MT5 terminal and verify they appear correctly through API endpoints

### Tests for User Story 5

- [ ] T056 [P] [US5] Write contract tests for positions/orders endpoints in tests/test_api/test_history.py
- [ ] T057 [P] [US5] Write integration tests for position monitoring in tests/test_api/test_integration.py

### Implementation for User Story 5

- [ ] T058 [P] [US5] Create request models (PositionsRequest, OrdersRequest) in pdmt5/api/models.py
- [ ] T059 [US5] Implement GET /api/v1/positions endpoint in pdmt5/api/routers/history.py
- [ ] T060 [US5] Implement GET /api/v1/orders endpoint in pdmt5/api/routers/history.py
- [ ] T061 [US5] Run tests and verify all US5 endpoints work with both formats
- [ ] T062 [US5] Run quality checks (ruff format, ruff check, pyright, pytest)

**Checkpoint**: All core user stories should now be independently functional

---

## Phase 7: Security & Production Readiness (Priority: P3)

**Purpose**: Add production-grade security and operational features

- [ ] T063 [P] Implement rate limiting using slowapi in pdmt5/api/middleware.py
- [ ] T064 [P] Add CORS middleware configuration in pdmt5/api/main.py
- [ ] T065 [P] Configure structured logging in pdmt5/api/main.py
- [ ] T066 [P] Write tests for rate limiting in tests/test_api/test_middleware.py
- [ ] T067 [P] Add API usage examples to docs/api/rest-api.md
- [ ] T068 Validate OpenAPI spec generation at /docs endpoint
- [ ] T069 Run comprehensive integration tests across all endpoints
- [ ] T070 Run quality checks (ruff format, ruff check, pyright, pytest) with 100% coverage verification

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T071 [P] Create deployment guide for Windows service in docs/api/deployment.md
- [ ] T072 [P] Add MkDocs page for API documentation in docs/api/index.md
- [ ] T073 [P] Update pdmt5/__init__.py to export API classes if needed
- [ ] T074 Verify quickstart.md examples work end-to-end
- [ ] T075 [P] Add performance benchmarks (health check <500ms, concurrent requests)
- [ ] T076 [P] Security audit (check for injection vulnerabilities, secure defaults)
- [ ] T077 Final quality check across all code (ruff format, ruff check, pyright, pytest)
- [ ] T078 Build and test documentation with mkdocs build

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P4 → P5)
- **Security (Phase 7)**: Can start after Foundation, parallel with user stories
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Independent of US1
- **User Story 4 (P4)**: Can start after Foundational - Independent of US1/US2
- **User Story 5 (P5)**: Can start after Foundational - Independent of other stories

Note: User Story 3 (Flexible Data Format Selection) is implemented in Phase 2 (Foundational) as it's cross-cutting infrastructure.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD mandatory per CLAUDE.md)
- Request models before endpoints
- Router implementation before registration
- Tests verify both JSON and Parquet formats
- Quality checks after each user story completion

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004)
- All Foundational model/formatter tasks marked [P] can run in parallel (T006-T011, T016-T018)
- Once Foundational phase completes, all user stories (US1-US5) can start in parallel
- Request model creation within each story can run in parallel
- Test file creation can run in parallel
- Documentation tasks in Polish phase can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T020: "Write contract tests for symbols endpoints"
Task T021: "Write contract tests for market data endpoints"
Task T022: "Write integration tests for symbol retrieval"

# Launch all request model creation for User Story 1 together:
Task T023: "Create SymbolsRequest, SymbolInfoRequest, SymbolTickRequest models"
Task T024: "Create RatesFromRequest, RatesFromPosRequest, RatesRangeRequest models"
Task T025: "Create TicksFromRequest, TicksRangeRequest, MarketBookRequest models"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T019) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T020-T037)
4. **STOP and VALIDATE**: Test User Story 1 independently with both formats
5. Deploy/demo if ready - API can serve market data!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T019)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - market data!) (T020-T037)
3. Add User Story 2 → Test independently → Deploy/Demo (account monitoring added) (T038-T046)
4. Add User Stories 4+5 → Test independently → Deploy/Demo (historical data + positions) (T047-T062)
5. Add Security features → Production-ready (T063-T070)
6. Polish → Documentation complete (T071-T078)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T019)
2. Once Foundational is done:
   - Developer A: User Story 1 (Market Data) (T020-T037)
   - Developer B: User Story 2 (Account Info) (T038-T046)
   - Developer C: User Stories 4+5 (History & Positions) (T047-T062)
   - Developer D: Security features (T063-T070)
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (T071-T078)

---

## Task Statistics

- **Total Tasks**: 78
- **Setup Tasks**: 4
- **Foundational Tasks**: 15
- **User Story 1 (P1)**: 18 tasks
- **User Story 2 (P2)**: 9 tasks
- **User Story 4 (P4)**: 9 tasks
- **User Story 5 (P5)**: 7 tasks
- **Security & Production**: 8 tasks
- **Polish & Documentation**: 8 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel

**MVP Scope** (Phases 1-3): 37 tasks → Market data API functional

**Production Ready** (Phases 1-7): 70 tasks → Full API with security

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story (US1-US5) for traceability
- Each user story is independently completable and testable
- TDD mandatory per CLAUDE.md: Write tests first, see them fail, then implement
- Run quality checks after each phase: `uv run ruff format . && uv run ruff check --fix . && uv run pyright . && uv run pytest tests/ -v`
- Target 100% test coverage (project standard)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 3 (Format Selection) is cross-cutting and implemented in Foundation phase
