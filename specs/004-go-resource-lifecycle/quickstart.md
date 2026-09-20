# Quickstart: Validate Go Resource Lifecycle

Run local-only tests from the repository root:

    OPENCODE_GO_API_KEY=placeholder .venv/bin/pytest -q tests/test_opencode_go_provider.py

Expected: owned clients close; injected clients remain open; graph/CLI cleanup
is idempotent; no HTTP request leaves the process.
