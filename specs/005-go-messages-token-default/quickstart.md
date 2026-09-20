# Quickstart: Validate the Go Messages Token Default

From the repository root, run:

```powershell
# Only affects this PowerShell process; does not write configuration or secrets.
$testKeyVars = @(
  "OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "XAI_API_KEY",
  "DEEPSEEK_API_KEY", "DASHSCOPE_API_KEY", "DASHSCOPE_CN_API_KEY",
  "ZHIPU_API_KEY", "ZHIPU_CN_API_KEY", "MINIMAX_API_KEY", "MINIMAX_CN_API_KEY",
  "OPENROUTER_API_KEY", "AZURE_OPENAI_API_KEY", "ALPHA_VANTAGE_API_KEY",
  "FRED_API_KEY", "OPENCODE_GO_API_KEY", "OPENAI_COMPATIBLE_API_KEY",
  "MISTRAL_API_KEY", "MOONSHOT_API_KEY", "GROQ_API_KEY", "NVIDIA_API_KEY",
  "AWS_BEARER_TOKEN_BEDROCK"
)
$testKeyVars | ForEach-Object { Set-Item "Env:$_" "placeholder" }
.\.venv\Scripts\python.exe -m pytest -q tests/test_opencode_go_provider.py tests/test_llm_max_tokens.py
.\.venv\Scripts\python.exe -m pytest -q
```

On POSIX shells, use:

```bash
env OPENAI_API_KEY=placeholder GOOGLE_API_KEY=placeholder ANTHROPIC_API_KEY=placeholder \
  XAI_API_KEY=placeholder DEEPSEEK_API_KEY=placeholder DASHSCOPE_API_KEY=placeholder \
  DASHSCOPE_CN_API_KEY=placeholder ZHIPU_API_KEY=placeholder ZHIPU_CN_API_KEY=placeholder \
  MINIMAX_API_KEY=placeholder MINIMAX_CN_API_KEY=placeholder OPENROUTER_API_KEY=placeholder \
  AZURE_OPENAI_API_KEY=placeholder ALPHA_VANTAGE_API_KEY=placeholder FRED_API_KEY=placeholder \
  OPENCODE_GO_API_KEY=placeholder OPENAI_COMPATIBLE_API_KEY=placeholder \
  MISTRAL_API_KEY=placeholder MOONSHOT_API_KEY=placeholder GROQ_API_KEY=placeholder \
  NVIDIA_API_KEY=placeholder AWS_BEARER_TOKEN_BEDROCK=placeholder \
  .venv/bin/python -m pytest -q tests/test_opencode_go_provider.py tests/test_llm_max_tokens.py
env OPENAI_API_KEY=placeholder GOOGLE_API_KEY=placeholder ANTHROPIC_API_KEY=placeholder \
  XAI_API_KEY=placeholder DEEPSEEK_API_KEY=placeholder DASHSCOPE_API_KEY=placeholder \
  DASHSCOPE_CN_API_KEY=placeholder ZHIPU_API_KEY=placeholder ZHIPU_CN_API_KEY=placeholder \
  MINIMAX_API_KEY=placeholder MINIMAX_CN_API_KEY=placeholder OPENROUTER_API_KEY=placeholder \
  AZURE_OPENAI_API_KEY=placeholder ALPHA_VANTAGE_API_KEY=placeholder FRED_API_KEY=placeholder \
  OPENCODE_GO_API_KEY=placeholder OPENAI_COMPATIBLE_API_KEY=placeholder \
  MISTRAL_API_KEY=placeholder MOONSHOT_API_KEY=placeholder GROQ_API_KEY=placeholder \
  NVIDIA_API_KEY=placeholder AWS_BEARER_TOKEN_BEDROCK=placeholder \
  .venv/bin/python -m pytest -q
```

The focused test must show that simulated Qwen and MiniMax Messages requests
include `8192` when no limit is configured, and that an explicit value replaces
it. The placeholder skips the credential-gated DeepSeek live test; these
commands use local fakes/transports and must not contact OpenCode or financial
services.
