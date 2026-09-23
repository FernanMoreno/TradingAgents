# Quickstart: Validate OpenCode Go Transport Hardening

These checks use a simulated key and only local client construction or in-process
HTTP transports. They do not send requests to OpenCode, another AI provider, or
financial services.

## Focused regression check

Run from the TradingAgents repository root:

    OPENCODE_GO_API_KEY=simulated .venv/bin/pytest -q tests/test_opencode_go_provider.py

Expected outcomes:

- A default direct Messages client has finite HTTP timeout phases.
- A finite explicit timeout and injected client retain their behavior.
- `OpenCode_Go` rejects a known tool-incompatible Quick model before startup
  effects, just like `opencode_go`.

## Full verification

Run the repository test and static-check commands without exposing a real Go
credential. The suite must use local proxy denial and simulated transports to
detect accidental external calls.
