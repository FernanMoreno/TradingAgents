# Data Model: Direct OpenCode Go Messages

## Go Messages Capability

| Field | Meaning | Invariant |
|---|---|---|
| `model_id` | Official OpenCode Go Messages identifier | Must exist in the strict Go model catalog. |
| `supports_tools` | Ordinary tool-call support | Defaults conservatively; enabled only by reviewed evidence. |
| `supports_forced_tool_choice` | Named schema-tool selection support | `False` unless the exact model is verified. |
| `supports_structured_output` | Typed result guarantee | True only when the required forced tool behavior is verified. |

Initial reviewed entries:

| Model | Tools | Forced tool choice | Structured output |
|---|---:|---:|---:|
| `minimax-m3` | yes | yes | yes |
| `qwen3.8-flash` | yes | no | no |

All other Messages models require explicit capability review before a forced
tool or typed structured-output path is enabled.

## Go Request

| Field | Owner | Invariant |
|---|---|---|
| endpoint | Go adapter | Exactly `https://opencode.ai/zen/go/v1/messages`. |
| API key | process environment | Read only from `OPENCODE_GO_API_KEY`; never serialized to logs. |
| user agent | Go adapter | Identifies TradingAgents truthfully. |
| session ID | graph run | Non-empty and stable for quick/deep calls in one run. |
| messages | caller/adapter | Converted without changing conversation order. |
| tools | caller/adapter | Converted to Messages tool schemas only when supported. |

## Go Response

| Field | Meaning | Adapter result |
|---|---|---|
| text block | User-visible response text | `AIMessage.content`. |
| thinking block | Model reasoning metadata | Retained as non-user-visible additional metadata. |
| tool-use block | Requested tool name, JSON input, ID | Standard LangChain `tool_calls`. |
| usage | Provider token accounting | Response usage metadata. |
| stop reason | Completion state | Response metadata. |

## State Transitions

```text
configured model
  -> validate model and session
  -> bind capability-safe tools or structured schema
  -> direct Go Messages request
  -> parse text/thinking/tool-use blocks
  -> TradingAgents tool routing or final response

unsupported structured capability
  -> bind_structured returns no structured runnable
  -> existing free-text Go invocation
```

No request mutates persistent application state. Authentication, quota, and
protocol errors are terminal for that Go request and do not transition to a
different provider.
