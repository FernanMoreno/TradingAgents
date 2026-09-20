# Quickstart: Validate the Go Messages Token Default

From the repository root, run:

```powershell
$env:DEEPSEEK_API_KEY = "placeholder"  # disables the repository's one live API test
$env:OPENCODE_GO_API_KEY = "placeholder"
pytest -q tests/test_opencode_go_provider.py tests/test_llm_max_tokens.py
pytest -q
```

On POSIX shells, use:

```bash
DEEPSEEK_API_KEY=placeholder OPENCODE_GO_API_KEY=placeholder \
  pytest -q tests/test_opencode_go_provider.py tests/test_llm_max_tokens.py
DEEPSEEK_API_KEY=placeholder OPENCODE_GO_API_KEY=placeholder pytest -q
```

The focused test must show that simulated Qwen and MiniMax Messages requests
include `4096` when no limit is configured, and that an explicit value replaces
it. The placeholder skips the credential-gated DeepSeek live test; these
commands use local fakes/transports and must not contact OpenCode or financial
services.
