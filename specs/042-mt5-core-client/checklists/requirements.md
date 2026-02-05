# Requirements Checklist: Mt5 Core Client

**Purpose**: Validate MT5 core client baseline against current code.
**Created**: 2026-02-05
**Feature**: ../spec.md

## Connectivity and lifecycle

- [ ] CHK001 Confirm context manager initializes and shuts down MT5 reliably.
- [ ] CHK002 Verify initialization checks and runtime errors when uninitialized.
- [ ] CHK003 Confirm MT5 last_error is logged with actionable context.

## Core data access

- [ ] CHK004 Validate account and terminal info helpers return dict outputs.
- [ ] CHK005 Validate symbol, tick, and rate retrieval helpers return data or empty results.
- [ ] CHK006 Validate market book and symbol group filtering helpers.

## Trading and history retrieval

- [ ] CHK007 Validate orders and positions retrieval for symbols, groups, tickets.
- [ ] CHK008 Validate history orders and deals retrieval for date ranges.
- [ ] CHK009 Confirm failures raise Mt5RuntimeError with operation name/status.
