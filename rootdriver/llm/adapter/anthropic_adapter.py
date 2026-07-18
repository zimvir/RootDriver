"""Anthropic 适配器。"""

import json
import os
from typing import Any
from ..base_adapter import BaseAdapter

from rootdriver.types import LLMRequest, LLMResponse, Message, Usage, Role
from rootdriver.types.tool import ToolDefinition, ToolCall


class AnthropicAdapter(BaseAdapter):
    """Anthropic 适配器：LLMRequest ↔ Anthropic API 格式。"""

    def __init__(self, api_key: str = None, base_url: str = None):
        from anthropic import Anthropic

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = base_url
        self.client = Anthropic(api_key=self.api_key, base_url=base_url or None)

    def request_to_provider(self, req: LLMRequest) -> dict:
        """LLMRequest → Anthropic API 格式。"""
        messages = []
        system_parts = []

        for msg in req.messages:
            if msg.role == Role.SYSTEM:
                # Anthropic 的 system 单独放
                system_parts.append({"type": "text", "text": msg.content})
            elif msg.role == Role.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == Role.ASSISTANT:
                content = msg.content
                # 处理 tool_calls
                if msg.tool_calls:
                    # 如果有 tool_calls，content 可能是空的
                    block = {"type": "text", "text": content or ""}
                    tool_calls_block = [
                        {
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments if isinstance(tc.arguments, dict) else json.loads(tc.arguments),
                        }
                        for tc in msg.tool_calls
                    ]
                    messages.append({"role": "assistant", "content": [block] + tool_calls_block})
                    continue
                messages.append({"role": "assistant", "content": content or ""})
            elif msg.role == Role.TOOL:
                # Tool result 需要跟在 assistant 的 tool_use 后面
                # 这里简化为直接作为 content
                messages.append({"role": "user", "content": f"[tool result id={msg.tool_call_id}] {msg.content}"})

        # 处理 system prompt
        system = None
        if system_parts:
            system = "\n".join(p["text"] for p in system_parts)
        elif req.messages and req.messages[0].role == Role.SYSTEM:
            system = req.messages[0].content

        payload: dict[str, Any] = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens or 4096,
        }
        if system:
            payload["system"] = system
        if req.temperature is not None:
            payload["temperature"] = req.temperature
        if req.tools:
            payload["tools"] = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.parameters,
                }
                for t in req.tools
            ]

        return payload

    def response_to_frame(self, resp: Any) -> LLMResponse:
        """Anthropic API 响应 → LLMResponse。"""
        # Anthropic 返回的 content 是 list of blocks
        content_text = ""
        tool_calls = []
        tool_results = []

        for block in resp.content:
            if block.type == "text":
                content_text += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )
            elif block.type == "tool_result":
                tool_results.append(block)

        message = Message(
            role=Role.ASSISTANT,
            content=content_text,
            created_at="",
        )
        if tool_calls:
            message.tool_calls = tool_calls

        usage = Usage(
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
            total_tokens=resp.usage.input_tokens + resp.usage.output_tokens,
        )

        return LLMResponse(
            id=resp.id,
            model=resp.model,
            message=message,
            usage=usage,
            created_at="",
        )

    def invoke(self, req: LLMRequest) -> LLMResponse:
        """发送请求并返回 LLMResponse。"""
        payload = self.request_to_provider(req)
        resp = self.client.messages.create(**payload)
        return self.response_to_frame(resp)

    async def ainvoke(self, req: LLMRequest) -> LLMResponse:
        """异步发送请求并返回 LLMResponse。"""
        payload = self.request_to_provider(req)
        # Anthropic SDK 的 create 是 sync 的，用 asyncio.to_thread 包装
        import asyncio
        resp = await asyncio.to_thread(self.client.messages.create, **payload)
        return self.response_to_frame(resp)
