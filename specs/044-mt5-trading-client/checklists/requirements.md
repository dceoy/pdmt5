# Requirements Checklist: Mt5 Trading Client

**Purpose**: Validate Mt5TradingClient behavior against current code.
**Created**: 2026-02-05
**Feature**: ../spec.md

## Position management

- [ ] CHK001 Confirm close positions by symbol/all returns structured results.
- [ ] CHK002 Confirm empty position lists yield empty results with warnings.

## Dry-run validation

- [ ] CHK003 Verify dry-run uses order_check and avoids live execution.
- [ ] CHK004 Verify live execution path when dry_run is false.

## Metrics and errors

- [ ] CHK005 Validate minimum margin, volume-by-margin, spread ratio outputs.
- [ ] CHK006 Validate position metrics DataFrame outputs.
- [ ] CHK007 Confirm trading errors raise Mt5TradingError with context.
