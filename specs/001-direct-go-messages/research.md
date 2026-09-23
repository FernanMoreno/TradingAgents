# Research: Direct OpenCode Go Messages

## Decision: Treat Messages as an OpenCode Go transport, not an Anthropic provider

**Rationale**: OpenCode Go documents its own `/zen/go/v1/messages` endpoint and
labels its SDK compatibility as `@ai-sdk/anthropic`. The endpoint, API key,
session header, usage limits, and routing remain OpenCode Go. A compatibility
wire format does not make Anthropic the selected provider.

**Evidence**: [Official Go documentation](https://opencode.ai/docs/go/) lists
the Messages endpoint per model and requires an own user-agent plus a stable
`x-opencode-session` for a conversation.

**Alternatives considered**:

- Keep `langchain_anthropic.ChatAnthropic` with a Go base URL: rejected because
  it retains an Anthropic SDK/client dependency in the Go path.
- Route Messages models through the OpenAI-compatible endpoint: rejected
  because the official Go endpoint table assigns these models to Messages.
- Remove Messages models: rejected because it discards available Go models
  rather than implementing their documented transport.

## Decision: Use a narrow direct LangChain chat model

**Rationale**: A `langchain_core` chat model can expose the existing
`invoke`, `bind_tools`, and `with_structured_output` surface while its transport
uses `httpx` directly. The new model owns only Go Messages serialization and
parsing; factory and graph ownership remain unchanged.

**Alternatives considered**:

- A standalone request helper outside LangChain: rejected because it would
  bypass existing agent and graph contracts.
- A generic proxy adapter: rejected because custom URLs are prohibited for Go
  and would weaken the no-external-host guarantee.

## Decision: Capabilities are model-specific and conservative

**Rationale**: Direct, minimal, non-financial requests to Go established:

- `minimax-m3` accepted a named forced tool and returned `tool_use`.
- `qwen3.8-flash` returned HTTP 400 for the same forced-tool request.
- `qwen3.8-flash` accepted an ordinary unforced tool and returned `thinking`
  and `tool_use` blocks.

The difference occurred through raw HTTP to `opencode.ai`, so it is not caused
by the Anthropic Python SDK. Untested Messages models must not inherit either
result merely because they share an endpoint.

After the direct adapter was implemented, one authorized non-financial smoke
request to `minimax-m3` asked for the exact coding-client response `OK` and
returned `OK` through `OpenCodeGoMessages`. It used the fixed Messages endpoint
and a non-secret stable session identifier. This validates only direct text
transport; tools, structured output, errors, and routing remain simulated to
avoid further quota consumption and market-data activity.

**Alternatives considered**:

- Force tools for every Messages model: rejected because it reproduces the
  known Qwen failure and spends a request before fallback.
- Use JSON prompting as structured-output equivalence: rejected because an
  earlier Qwen `json_schema` response did not honor a tested literal constraint.
- Disable all tools for all Messages models: rejected because both tested
  models demonstrate ordinary tool support and MiniMax demonstrates forced
  tools.

## Decision: Preserve the existing structured free-text fallback

**Rationale**: For a model without verified forced-schema support, the direct
adapter will report structured output as unsupported at binding time. The
existing `bind_structured` helper then selects its regular Go free-text path;
it does not switch provider and it avoids a predictable failed request.

## Dependency and documentation notes

- `httpx` must be declared directly because the new adapter owns its transport;
  relying on it only as a transitive dependency is not stable.
- The repository keeps `langchain-anthropic` and `anthropic` for the existing
  separately selected Anthropic provider. The requirement is to remove them
  from the `opencode_go` Messages path, not to remove that existing provider.
- Context7 was not available in this session. The primary official OpenCode
  documentation and the installed LangChain interfaces were used instead;
  no undocumented model ID or endpoint is assumed.

## Graphify impact refresh

The final code-only graph covered 15 client files, 189 nodes, 311 edges, and
11 communities. Its extracted call edges show
`create_llm_client -> OpenCodeGoClient -> OpenCodeGoMessages`, with
`OpenCodeGoMessages.with_structured_output -> bind_tools`. `AnthropicClient`
remains a separate factory branch; no extracted import or call edge enters it
from the Go Messages branch. Generated graph artifacts are intentionally not
tracked.
