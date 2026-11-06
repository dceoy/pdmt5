---
name: metatrader5-docs
description: Search the official MQL5 documentation for MetaTrader5 Python package usage. Use whenever the user asks about MT5 Python API functions (initialize, copy_rates_*, order_send, positions_get, etc.), their parameters, return values, error codes, or usage examples, even if they do not mention the docs explicitly.
---

# MetaTrader5 Python Documentation Search

Answer from the official MQL5 documentation at `https://www.mql5.com/en/docs/python_metatrader5`, fetched fresh, not from memory.

## Procedure

1. Identify the relevant MT5 Python function(s). For a general or unclear query, fetch the index page first.
2. Look up each function's URL path in [references/function-index.md](references/function-index.md) and append it to the base URL. When a query spans several functions, fetch the pages in parallel if the tooling allows.
3. Fetch each page with the agent's native web-fetch or browser tool. Fall back to `curl -fsSL "<url>"` only if none exists.
4. Extract the signature, parameter names, types and descriptions, return value, remarks, and the full code example.
5. If a page fails to load, the function is missing from the index, or the network is blocked, say so, link the index page, and answer from known behavior marked as unverified.

## Response Format

For each function, give:

1. **Function**: `MetaTrader5.function_name()`
2. **Description**: what it does
3. **Signature**: full call signature
4. **Parameters**: name, type, and meaning
5. **Returns**: type and meaning
6. **Example**: the documentation's code example
7. **Source**: link to the documentation page

Drop sections the page does not cover instead of padding them.
