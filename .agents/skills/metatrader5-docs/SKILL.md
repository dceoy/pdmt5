---
name: metatrader5-docs
description: Search the official MQL5 documentation for MetaTrader5 Python package usage. Use when the user needs help with MT5 Python API functions, parameters, return values, or usage examples.
---

# MetaTrader5 Python Documentation Search

Search the official MQL5 documentation at `https://www.mql5.com/en/docs/python_metatrader5` for MetaTrader5 Python package usage.

## Agent-Agnostic Compatibility

This skill is **agent-agnostic** and can be used with Claude Code, Codex CLI, Copilot CLI, or other agents.

- Prefer the agent's native web-fetch capability (for example: `WebFetch`, browser tool, or built-in URL retrieval).
- If no native fetch tool exists, use CLI fallback (`curl` or `wget`) to retrieve docs pages.
- If network access is blocked, state the limitation and provide the best guidance from known MT5 docs structure.

## Procedure

1. Identify the MT5 Python function(s) relevant to the user's query.
2. Fetch the corresponding documentation page(s) using the available web retrieval method.
3. Summarize the function signature, parameters, return value, and usage examples.
4. If the user's query is general or unclear, fetch the index page first to find the right function.

## Documentation URL Map

Base URL: `https://www.mql5.com/en/docs/python_metatrader5`

| Function               | URL Path                    |
| ---------------------- | --------------------------- |
| `initialize`           | `/mt5initialize_py`         |
| `login`                | `/mt5login_py`              |
| `shutdown`             | `/mt5shutdown_py`           |
| `version`              | `/mt5version_py`            |
| `last_error`           | `/mt5lasterror_py`          |
| `account_info`         | `/mt5accountinfo_py`        |
| `terminal_info`        | `/mt5terminalinfo_py`       |
| `symbols_total`        | `/mt5symbolstotal_py`       |
| `symbols_get`          | `/mt5symbolsget_py`         |
| `symbol_info`          | `/mt5symbolinfo_py`         |
| `symbol_info_tick`     | `/mt5symbolinfotick_py`     |
| `symbol_select`        | `/mt5symbolselect_py`       |
| `market_book_add`      | `/mt5marketbookadd_py`      |
| `market_book_get`      | `/mt5marketbookget_py`      |
| `market_book_release`  | `/mt5marketbookrelease_py`  |
| `copy_rates_from`      | `/mt5copyratesfrom_py`      |
| `copy_rates_from_pos`  | `/mt5copyratesfrompos_py`   |
| `copy_rates_range`     | `/mt5copyratesrange_py`     |
| `copy_ticks_from`      | `/mt5copyticksfrom_py`      |
| `copy_ticks_range`     | `/mt5copyticksrange_py`     |
| `orders_total`         | `/mt5orderstotal_py`        |
| `orders_get`           | `/mt5ordersget_py`          |
| `order_calc_margin`    | `/mt5ordercalcmargin_py`    |
| `order_calc_profit`    | `/mt5ordercalcprofit_py`    |
| `order_check`          | `/mt5ordercheck_py`         |
| `order_send`           | `/mt5ordersend_py`          |
| `positions_total`      | `/mt5positionstotal_py`     |
| `positions_get`        | `/mt5positionsget_py`       |
| `history_orders_total` | `/mt5historyorderstotal_py` |
| `history_orders_get`   | `/mt5historyordersget_py`   |
| `history_deals_total`  | `/mt5historydealstotal_py`  |
| `history_deals_get`    | `/mt5historydealsget_py`    |

## Function Categories

Use these categories to narrow down the user's query:

- **Connection**: `initialize`, `login`, `shutdown`
- **Information**: `version`, `last_error`, `account_info`, `terminal_info`
- **Symbols**: `symbols_total`, `symbols_get`, `symbol_info`, `symbol_info_tick`, `symbol_select`
- **Market Depth**: `market_book_add`, `market_book_get`, `market_book_release`
- **Market Data**: `copy_rates_from`, `copy_rates_from_pos`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`
- **Orders**: `orders_total`, `orders_get`, `order_calc_margin`, `order_calc_profit`, `order_check`, `order_send`
- **Positions**: `positions_total`, `positions_get`
- **History**: `history_orders_total`, `history_orders_get`, `history_deals_total`, `history_deals_get`

## Fetching Documentation

For each relevant function, retrieve its documentation using whichever method the agent supports:

- Native fetch tools (preferred).
- Browser automation tools.
- Shell fallback, for example:

```bash
curl -fsSL "https://www.mql5.com/en/docs/python_metatrader5<url_path>"
```

Extraction target for each page:

- Function signature with all parameters.
- Parameter descriptions and types.
- Return value description.
- Notes/remarks.
- Full code example.

When the query spans multiple functions, fetch pages in parallel when the agent/tooling supports it.

## Response Format

Present the results as:

1. **Function**: `MetaTrader5.function_name()`
2. **Description**: What the function does
3. **Signature**: Full call signature with parameters
4. **Parameters**: Table or list of parameter names, types, and descriptions
5. **Returns**: Return type and description
6. **Example**: Code example from the documentation
7. **Source**: Link to the official documentation page
