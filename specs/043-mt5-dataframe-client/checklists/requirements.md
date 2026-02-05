# Requirements Checklist: Mt5 DataFrame Client

**Purpose**: Validate Mt5DataClient and configuration behavior against current code.
**Created**: 2026-02-05
**Feature**: ../spec.md

## DataFrame outputs

- [ ] CHK001 Confirm MT5 data retrieval methods return DataFrames.
- [ ] CHK002 Verify datetime conversion defaults and opt-out behavior.
- [ ] CHK003 Verify DataFrame index setting for non-empty results.

## Configuration and validation

- [ ] CHK004 Validate Mt5Config rejects invalid login/server/password types.
- [ ] CHK005 Validate input range/count checks for rates/ticks/history queries.
- [ ] CHK006 Confirm empty MT5 responses return empty DataFrames with schemas.

## Error handling

- [ ] CHK007 Confirm MT5 errors raise runtime errors with context.
