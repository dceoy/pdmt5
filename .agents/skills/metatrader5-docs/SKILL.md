---
name: metatrader5-docs
description: Search the official MQL5 documentation for MetaTrader5 Python package usage. Use whenever the user asks about MT5 Python API functions (initialize, copy_rates_*, order_send, positions_get, etc.), their parameters, return values, error codes, or usage examples, even if they do not mention the docs explicitly.
---

# MetaTrader5 Python Documentation Search

Search the official MQL5 documentation at `https://www.mql5.com/en/docs/python_metatrader5` for MetaTrader5 Python package usage.

## Agent-Agnostic Compatibility

- Prefer the agent's native web-fetch capability (for example: `WebFetch`, browser tool, or built-in URL retrieval).
- If no native fetch tool exists, use CLI fallback (`curl` or `wget`) to retrieve docs pages.
- If network access is blocked, state the limitation and provide the best guidance from known MT5 docs structure.

## Procedure

1. Identify the MT5 Python function(s) relevant to the user's query.
2. Fetch the corresponding documentation page(s) using the available web retrieval method.
3. Summarize the function signature, parameters, return value, and usage examples.
4. If the user's query is general or unclear, fetch the index page first to find the right function.
5. If a page fails to load or a function is missing from the index, say so, link the index page, and answer from known behavior while marking it as unverified.

## Function Index

Read [references/function-index.md](references/function-index.md) to map a function name or category to its URL path. Append the path to the base URL `https://www.mql5.com/en/docs/python_metatrader5`.

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
