# Requirements Checklist: MT5 client operations

**Purpose**: Verify the baseline MT5 client operations spec against the current code.
**Created**: 2026-02-05
**Feature**: ../spec.md

## Core connectivity

- [ ] CHK001 Validate initialization/login flows with optional credentials.
- [ ] CHK002 Confirm MT5 operations require initialization and log last status.
- [ ] CHK003 Ensure runtime errors include MT5 last_error context.

## Data access

- [ ] CHK004 Confirm dict and DataFrame helpers exist for symbols, rates, ticks,
      orders, positions, and history endpoints.
- [ ] CHK005 Verify time conversion helpers apply to dict/list/DataFrame outputs
      with opt-out toggle.
- [ ] CHK006 Verify DataFrame index-setting behavior for non-empty results.
- [ ] CHK007 Validate input checks for counts, dates, positions, and positive
      numeric values.

## Trading operations

- [ ] CHK008 Confirm order check/send helpers return structured dict/DF outputs.
- [ ] CHK009 Validate dry-run and raise-on-error behaviors for trading requests.
- [ ] CHK010 Confirm trading metrics (margin, spread ratio, position metrics)
      are computed and logged.
- [ ] CHK011 Validate convenience fetches (latest rates/ticks, entry deals) are
      available and documented.
