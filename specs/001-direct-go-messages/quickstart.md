# Quickstart: Validate Direct OpenCode Go Messages

## Prerequisites

- Work from the repository root.
- Use the project environment with test dependencies installed.
- Do not set or print a production key for simulated tests.

## Targeted simulated validation

```powershell
$env:TZ = "UTC"
python -m pytest -q tests/test_opencode_go_provider.py
python -m ruff check tradingagents cli tests
```

Expected outcomes:

- Messages requests are captured only at the fixed Go endpoint.
- The direct Go Messages module has no `anthropic` or `langchain_anthropic`
  import.
- `minimax-m3` can bind the verified forced structured schema.
- `qwen3.8-flash` uses ordinary tools but takes the free-text structured-result
  path without a forced-tool request.
- Auth and quota tests expose redacted Go errors and record one request.

## Regression and composed workflow validation

```powershell
$env:TZ = "UTC"
python -m pytest -q
project-composition-check "$(Get-Content .ai/project-name)"
```

If the composition helper or `.ai/project-name` is absent, record that absence
and run the repository's available architecture and integration checks instead.

## Optional real smoke check

Only run this when the user has explicitly authorized a real non-financial Go
request. Use a short neutral prompt and a new stable session identifier. Never
run a financial analysis, submit an order, print `OPENCODE_GO_API_KEY`, or use a
different provider as a fallback.
