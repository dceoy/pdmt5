---
name: local-qa
description: Run local QA including formatting, linting, and testing for the repository. Use whenever any file has been updated.
disable-model-invocation: true
---

# Local QA (format, lint, and test)

Run the local QA script from the directory of this file:

```bash
./scripts/qa.sh
```

## Procedure

- Execute the script exactly as shown above when this skill is triggered.
- Capture and summarize key output (success/failure, major warnings, and any files modified).
- If the script fails due to missing tooling, report the missing tool(s) and stop unless the user asks to install or fix them.
- Do not run additional commands unless the user requests them.
