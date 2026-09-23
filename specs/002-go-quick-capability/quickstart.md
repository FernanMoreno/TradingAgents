# Quickstart: Validate Go Quick Role Eligibility

These checks use no OpenCode credential and send no network request.

## Prerequisites

- Activate the project's Python environment.
- Run commands from the TradingAgents repository root.

## Focused regression check

Run:

    pytest -q tests/test_opencode_go_provider.py -k "quick or catalog or graph"

Expected outcomes:

- Quick omits the six reviewed Messages models without ordinary tools.
- Deep retains those IDs.
- A direct invalid Go Quick configuration stops before AI-client construction
  and startup side effects.

## Compatibility check

Run:

    pytest -q tests/test_opencode_go_provider.py tests/test_cli_prefs.py tests/test_model_validation.py

Expected outcomes:

- Valid Go models retain their existing provider path.
- Saved invalid Go Quick preferences are discarded by the shared selector.
- Existing strict unknown-model validation remains unchanged.

## Full verification

Run the repository test and static-check commands specified by the project
configuration. Do not set an OpenCode credential for these simulated checks.
