"""OpenAI 适配器。"""

import json
import os
from typing import Any
from ..base_adapter import BaseAdapter
import openai

from rootdriver.types import LLMRequest, LLMResponse, Message, Usage, Role
from rootdriver.types.tool import ToolDefinition


class OpenAIAdapter(BaseAdapter):
    """OpenAI 适配器：LLMRequest ↔ OpenAI API 格式。"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "")
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url or None)
        self.async_client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url or None)

    def request_to_provider(self, req: LLMRequest) -> dict:
        """LLMRequest → OpenAI API 格式。"""
        messages = []
        for msg in req.messages:
            m = {"role": msg.role.value if isinstance(msg.role, Role) else msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            messages.append(m)

        payload: dict[str, Any] = {
            "model": req.model,
            "messages": messages,
            "temperature": req.temperature,
        }
        if req.max_tokens is not None:
            payload["max_tokens"] = req.max_tokens
        if req.tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in req.tools
            ]

        return payload

    def response_to_frame(self, resp: Any) -> LLMResponse:
        """OpenAI API 响应 → LLMResponse。"""
        choice = resp.choices[0]
        msg_data = choice.message

        message = Message(
            role=msg_data.role,
            content=msg_data.content,
            created_at=resp.created and str(resp.created) or "",
        )

        if msg_data.tool_calls:
            from rootdriver.types.tool import ToolCall

            def _parse_args(arg):
                if isinstance(arg, str):
                    return json.loads(arg)
                return arg or {}

            message.tool_calls = [
                ToolCall(id=tc.id, name=tc.function.name, arguments=_parse_args(tc.function.arguments))
                for tc in msg_data.tool_calls
            ]

        usage = Usage(
            prompt_tokens=resp.usage.prompt_tokens,
            completion_tokens=resp.usage.completion_tokens,
            total_tokens=resp.usage.total_tokens,
        )

        return LLMResponse(
            id=resp.id,
            model=resp.model,
            message=message,
            usage=usage,
            created_at=str(resp.created),
        )

    def invoke(self, req: LLMRequest) -> LLMResponse:
        """发送请求并返回 LLMResponse。"""
        payload = self.request_to_provider(req)
        resp = self.client.chat.completions.create(**payload)
        return self.response_to_frame(resp)

    async def ainvoke(self, req: LLMRequest) -> LLMResponse:
        """异步发送请求并返回 LLMResponse。"""
        payload = self.request_to_provider(req)
        resp = await self.async_client.chat.completions.create(**payload)
        return self.response_to_frame(resp)