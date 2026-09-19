# Contract: OpenCode Go Messages Adapter

## Construction

`OpenCodeGoClient(model, session_id=...).get_llm()` returns a direct Messages
chat model when the official catalog maps `model` to the Messages protocol.

The returned model:

- accepts the existing LangChain message inputs used by TradingAgents;
- exposes normal tool calls as standardized `AIMessage.tool_calls`;
- sends requests only to the fixed Go Messages URL;
- rejects a missing Go key, empty session ID, unknown model, or custom backend
  before a network request;
- maps HTTP 401/403/429 to the established redacted Go errors.

## Tool Contract

For a capability-enabled model, `bind_tools` converts the existing tool schema
to Go Messages tool definitions. A returned `tool_use` block must provide:

```text
name: string
args: object
id: string
type: "tool_call"
```

Named tool forcing is emitted only if the exact selected model advertises that
capability.

## Structured Output Contract

- A model with verified forced-schema support returns the existing typed schema
  result.
- A model without it raises `NotImplementedError` during binding, allowing the
  existing `bind_structured` helper to select free-text generation before any
  failed request.
- The fallback remains within the selected Go model and cannot select another
  provider.

## Protocol Failure Contract

Malformed top-level responses, missing content arrays, invalid tool inputs, or
unknown block types raise an OpenCode Go protocol error that contains no API key
or raw authorization data. The adapter does not retry a quota response and does
not make a second request on a parsing failure.
