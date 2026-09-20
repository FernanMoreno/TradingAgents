"""Direct LangChain transport for OpenCode Go Messages models.

OpenCode Go exposes a Messages-compatible wire format for some models.  This
module speaks that HTTP contract itself: importing or constructing an Anthropic
SDK client here would obscure provider ownership and make Go depend on an
unrelated client implementation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, Field, PrivateAttr


class OpenCodeGoProtocolError(RuntimeError):
    """A Go response did not satisfy the documented Messages contract."""

    is_terminal_provider_error = True


class OpenCodeGoMessages(BaseChatModel):
    """Minimal direct Messages client used by the OpenCode Go provider only."""

    model: str
    base_url: str
    api_key: str = Field(repr=False)
    default_headers: dict[str, str] = Field(default_factory=dict)
    max_retries: int = 0
    timeout: float | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    supports_tools: bool = False
    supports_forced_tool_choice: bool = False
    supports_structured_output: bool = False
    http_client: Any | None = Field(default=None, exclude=True)
    http_async_client: Any | None = Field(default=None, exclude=True)
    error_classifier: Callable[[Exception], Exception] = Field(exclude=True)
    _owned_client: httpx.Client | None = PrivateAttr(default=None)

    @property
    def _llm_type(self) -> str:
        return "opencode-go-messages"

    def _client(self) -> Any:
        if self.http_client is not None:
            return self.http_client
        if self._owned_client is None:
            # Passing timeout=None disables every HTTPX timeout phase. Omit the
            # argument instead so HTTPX supplies its finite default; explicit
            # caller-provided timeouts remain unchanged.
            if self.timeout is None:
                self._owned_client = httpx.Client()
            else:
                self._owned_client = httpx.Client(timeout=self.timeout)
        return self._owned_client

    @staticmethod
    def _serialize_tool(tool: Any) -> dict[str, Any]:
        """Translate LangChain's OpenAI-shaped tool definition to Messages."""
        if isinstance(tool, dict) and {"name", "input_schema"} <= tool.keys():
            return {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool["input_schema"],
            }
        try:
            function = convert_to_openai_tool(tool)["function"]
            return {
                "name": function["name"],
                "description": function.get("description", ""),
                "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
            }
        except (KeyError, TypeError, ValueError) as error:
            raise OpenCodeGoProtocolError(
                "OpenCode Go could not serialize a LangChain tool definition."
            ) from error

    @staticmethod
    def _serialize_tool_choice(tool_choice: Any) -> dict[str, str] | None:
        if tool_choice is None:
            return None
        if isinstance(tool_choice, str) and tool_choice in {"auto", "any"}:
            return {"type": tool_choice}
        if isinstance(tool_choice, str):
            return {"type": "tool", "name": tool_choice}
        if isinstance(tool_choice, dict):
            if tool_choice.get("type") == "tool" and isinstance(tool_choice.get("name"), str):
                return {"type": "tool", "name": tool_choice["name"]}
            function = tool_choice.get("function", {})
            if tool_choice.get("type") == "function" and isinstance(function.get("name"), str):
                return {"type": "tool", "name": function["name"]}
        raise OpenCodeGoProtocolError("Unsupported OpenCode Go Messages tool_choice.")

    def bind_tools(self, tools: list[Any], *, tool_choice: Any = None, **kwargs: Any) -> Any:
        """Bind Messages-native tools while retaining LangChain's Runnable API."""
        if not self.supports_tools:
            raise NotImplementedError(
                f"{self.model} has no verified OpenCode Go Messages tool support."
            )
        serialized_choice = self._serialize_tool_choice(tool_choice)
        if (
            serialized_choice is not None
            and serialized_choice["type"] == "tool"
            and not self.supports_forced_tool_choice
        ):
            raise NotImplementedError(
                f"{self.model} does not support OpenCode Go Messages forced tool choice."
            )
        return self.bind(
            tools=[self._serialize_tool(tool) for tool in tools],
            tool_choice=serialized_choice,
            **kwargs,
        )

    def with_structured_output(
        self, schema: Any, *, include_raw: bool = False, **kwargs: Any
    ) -> Any:
        """Parse a named Messages tool call as a structured LangChain value."""
        if not self.supports_structured_output:
            raise NotImplementedError(
                f"{self.model} does not support OpenCode Go Messages forced tool choice; "
                "structured agent factories will use free-text output."
            )
        if include_raw:
            raise NotImplementedError(
                "OpenCode Go Messages does not implement include_raw structured output."
            )
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise OpenCodeGoProtocolError(
                f"Unsupported OpenCode Go structured-output options: {unexpected}."
            )
        try:
            tool_name = convert_to_openai_tool(schema)["function"]["name"]
        except (KeyError, TypeError, ValueError) as error:
            raise OpenCodeGoProtocolError(
                "OpenCode Go could not derive a structured-output tool name."
            ) from error
        bound = self.bind_tools([schema], tool_choice=tool_name)
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return bound | PydanticToolsParser(tools=[schema], first_tool_only=True)
        return bound | JsonOutputKeyToolsParser(
            key_name=tool_name,
            first_tool_only=True,
        )

    def _payload(
        self,
        messages: list[BaseMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        serialized_messages: list[dict[str, Any]] = []
        system_parts: list[str] = []
        for message in messages:
            if isinstance(message, SystemMessage):
                if not isinstance(message.content, str):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go Messages only supports string system prompts."
                    )
                system_parts.append(message.content)
                continue
            if isinstance(message, HumanMessage):
                serialized_messages.append({"role": "user", "content": message.content})
                continue
            if isinstance(message, AIMessage):
                content: list[dict[str, Any]] = []
                preserved_blocks = message.additional_kwargs.get(
                    "opencode_go_content_blocks", []
                )
                if not isinstance(preserved_blocks, list):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go stored invalid assistant content blocks."
                    )
                content.extend(preserved_blocks)
                if isinstance(message.content, str) and message.content:
                    content.append({"type": "text", "text": message.content})
                elif not isinstance(message.content, str):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go Messages only supports string assistant content."
                    )
                for tool_call in message.tool_calls:
                    name = tool_call.get("name")
                    tool_id = tool_call.get("id")
                    arguments = tool_call.get("args")
                    if not isinstance(name, str) or not isinstance(tool_id, str) or not isinstance(arguments, dict):
                        raise OpenCodeGoProtocolError(
                            "OpenCode Go received an invalid LangChain tool call."
                        )
                    content.append(
                        {
                            "type": "tool_use",
                            "id": tool_id,
                            "name": name,
                            "input": arguments,
                        }
                    )
                serialized_messages.append({"role": "assistant", "content": content})
                continue
            if isinstance(message, ToolMessage):
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": message.tool_call_id,
                    "content": message.content,
                }
                if (
                    serialized_messages
                    and serialized_messages[-1]["role"] == "user"
                    and isinstance(serialized_messages[-1]["content"], list)
                ):
                    serialized_messages[-1]["content"].append(tool_result)
                else:
                    serialized_messages.append({"role": "user", "content": [tool_result]})
                continue
            raise OpenCodeGoProtocolError(
                f"OpenCode Go Messages does not support {type(message).__name__}."
            )

        payload: dict[str, Any] = {"model": self.model, "messages": serialized_messages}
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        return payload

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        if stop:
            raise OpenCodeGoProtocolError("OpenCode Go Messages does not accept stop sequences yet.")
        allowed_kwargs = {"tools", "tool_choice"}
        unsupported_kwargs = set(kwargs) - allowed_kwargs
        if unsupported_kwargs:
            unexpected = ", ".join(sorted(unsupported_kwargs))
            raise OpenCodeGoProtocolError(
                f"Unsupported OpenCode Go Messages invocation options: {unexpected}."
            )
        try:
            response = self._client().post(
                self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    **self.default_headers,
                },
                json=self._payload(
                    messages,
                    tools=kwargs.get("tools"),
                    tool_choice=kwargs.get("tool_choice"),
                ),
            )
            response.raise_for_status()
        except Exception as error:
            classified = self.error_classifier(error)
            if classified is error:
                raise
            raise classified from error

        try:
            data = response.json()
            blocks = data["content"]
        except (KeyError, TypeError, ValueError) as error:
            raise OpenCodeGoProtocolError(
                "OpenCode Go returned a malformed Messages response."
            ) from error
        if not isinstance(blocks, list):
            raise OpenCodeGoProtocolError(
                "OpenCode Go returned a Messages response whose content is not a list."
            )

        text_blocks = []
        tool_calls = []
        preserved_blocks = []
        for block in blocks:
            if not isinstance(block, dict):
                raise OpenCodeGoProtocolError(
                    "OpenCode Go returned a Messages content block that is not an object."
                )
            if block.get("type") == "text":
                text = block.get("text", "")
                if not isinstance(text, str):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go returned an invalid Messages text block."
                    )
                text_blocks.append(text)
                continue
            if block.get("type") == "thinking":
                thinking = block.get("thinking")
                signature = block.get("signature")
                if not isinstance(thinking, str) or not isinstance(signature, str):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go returned an invalid Messages thinking block."
                    )
                preserved_blocks.append(
                    {"type": "thinking", "thinking": thinking, "signature": signature}
                )
                continue
            if block.get("type") == "tool_use":
                tool_id = block.get("id")
                name = block.get("name")
                arguments = block.get("input")
                if not isinstance(tool_id, str) or not isinstance(name, str) or not isinstance(arguments, dict):
                    raise OpenCodeGoProtocolError(
                        "OpenCode Go returned an invalid Messages tool_use block."
                    )
                tool_calls.append({"name": name, "args": arguments, "id": tool_id})
                continue
            raise OpenCodeGoProtocolError("OpenCode Go returned an unsupported Messages block type.")

        text = "".join(text_blocks)
        usage_metadata = None
        usage = data.get("usage")
        if isinstance(usage, dict):
            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")
            if isinstance(input_tokens, int) and isinstance(output_tokens, int):
                total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
                if isinstance(total_tokens, int):
                    usage_metadata = {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": total_tokens,
                    }
        message = AIMessage(
            content=text,
            additional_kwargs=(
                {"opencode_go_content_blocks": preserved_blocks}
                if preserved_blocks
                else {}
            ),
            response_metadata={
                "id": data.get("id"),
                "model": data.get("model"),
                "stop_reason": data.get("stop_reason"),
            },
            tool_calls=tool_calls,
            usage_metadata=usage_metadata,
        )
        return ChatResult(generations=[ChatGeneration(message=message)])
