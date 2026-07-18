"""Anthropic 适配器测试。"""

import pytest
from unittest.mock import MagicMock, patch

from rootdriver.llm.adapter.anthropic_adapter import AnthropicAdapter
from rootdriver.types import LLMRequest, Message, Usage, Role
from rootdriver.types.tool import ToolDefinition


@pytest.fixture
def adapter():
    """创建适配器实例。"""
    return AnthropicAdapter(api_key="test_key", base_url="https://api.minimaxi.com/anthropic")


@pytest.fixture
def llm_request():
    """创建 LLMRequest。"""
    return LLMRequest(
        model="claude-sonnet-4-20250514",
        messages=[
            Message(role=Role.SYSTEM, content="You are a helpful assistant", created_at="2026-01-01T00:00:00"),
            Message(role=Role.USER, content="hello", created_at="2026-01-01T00:00:01"),
        ],
        temperature=0.7,
        max_tokens=1024,
    )


@pytest.fixture
def llm_request_with_tools():
    """创建带工具的 LLMRequest。"""
    return LLMRequest(
        model="claude-sonnet-4-20250514",
        messages=[
            Message(role=Role.USER, content="北京天气怎么样？", created_at="2026-01-01T00:00:00"),
        ],
        tools=[
            ToolDefinition(
                name="get_weather",
                description="获取城市天气",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "城市名称"},
                    },
                    "required": ["city"],
                },
            )
        ],
        max_tokens=1024,
    )


class TestAnthropicAdapterRequestToProvider:
    """测试 request_to_provider 方法。"""

    def test_basic_request(self, adapter, llm_request):
        payload = adapter.request_to_provider(llm_request)

        assert payload["model"] == "claude-sonnet-4-20250514"
        assert payload["max_tokens"] == 1024
        assert payload["temperature"] == 0.7
        assert "system" in payload
        assert "You are a helpful assistant" in payload["system"]

    def test_system_prompt_extraction(self, adapter):
        req = LLMRequest(
            model="claude-3",
            messages=[
                Message(role=Role.SYSTEM, content="You are customer service", created_at=""),
                Message(role=Role.USER, content="question", created_at=""),
            ],
        )
        payload = adapter.request_to_provider(req)

        assert payload["system"] == "You are customer service"
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "question"

    def test_user_message(self, adapter):
        req = LLMRequest(
            model="claude-3",
            messages=[Message(role=Role.USER, content="hello", created_at="")],
        )
        payload = adapter.request_to_provider(req)

        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "hello"

    def test_assistant_message(self, adapter):
        req = LLMRequest(
            model="claude-3",
            messages=[Message(role=Role.ASSISTANT, content="回答", created_at="")],
        )
        payload = adapter.request_to_provider(req)

        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "assistant"
        assert payload["messages"][0]["content"] == "回答"

    def test_tools_conversion(self, adapter, llm_request_with_tools):
        payload = adapter.request_to_provider(llm_request_with_tools)

        assert "tools" in payload
        assert len(payload["tools"]) == 1
        assert payload["tools"][0]["name"] == "get_weather"
        assert payload["tools"][0]["description"] == "获取城市天气"
        assert payload["tools"][0]["input_schema"]["type"] == "object"

    def test_tool_calls_in_request(self, adapter):
        from rootdriver.types.tool import ToolCall

        req = LLMRequest(
            model="claude-3",
            messages=[
                Message(
                    role=Role.ASSISTANT,
                    content="好的，我来查一下",
                    tool_calls=[
                        ToolCall(id="call_123", name="get_weather", arguments={"city": "北京"})
                    ],
                    created_at="",
                )
            ],
        )
        payload = adapter.request_to_provider(req)

        assert len(payload["messages"]) == 1
        msg = payload["messages"][0]
        assert msg["role"] == "assistant"
        assert isinstance(msg["content"], list)
        # 应该有 text block 和 tool_use block
        assert any(b["type"] == "text" for b in msg["content"])
        assert any(b["type"] == "tool_use" and b["name"] == "get_weather" for b in msg["content"])

    def test_max_tokens_default(self, adapter):
        req = LLMRequest(
            model="claude-3",
            messages=[Message(role=Role.USER, content="hi", created_at="")],
        )
        payload = adapter.request_to_provider(req)

        assert payload["max_tokens"] == 4096  # 默认值

    def test_temperature_with_value(self, adapter):
        req = LLMRequest(
            model="claude-3",
            messages=[Message(role=Role.USER, content="hi", created_at="")],
            temperature=0.9,
        )
        payload = adapter.request_to_provider(req)

        assert payload["temperature"] == 0.9


class TestAnthropicAdapterResponseToFrame:
    """测试 response_to_frame 方法。"""

    def test_basic_response(self, adapter):
        # 模拟 Anthropic 响应
        mock_resp = MagicMock()
        mock_resp.id = "msg_123"
        mock_resp.model = "claude-sonnet-4-20250514"
        mock_resp.content = [MagicMock(type="text", text="你好，我是助手")]
        mock_resp.usage.input_tokens = 100
        mock_resp.usage.output_tokens = 50

        result = adapter.response_to_frame(mock_resp)

        assert result.id == "msg_123"
        assert result.model == "claude-sonnet-4-20250514"
        assert result.message.content == "你好，我是助手"
        assert result.message.role == Role.ASSISTANT
        assert result.usage.prompt_tokens == 100
        assert result.usage.completion_tokens == 50

    def test_response_with_tool_calls(self, adapter):
        mock_resp = MagicMock()
        mock_resp.id = "msg_456"
        mock_resp.model = "claude-sonnet-4-20250514"

        # 创建 text block mock
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "我来查一下天气"

        # 创建 tool_use block mock
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "toolu_123"
        tool_block.name = "get_weather"
        tool_block.input = {"city": "北京"}

        mock_resp.content = [text_block, tool_block]
        mock_resp.usage.input_tokens = 80
        mock_resp.usage.output_tokens = 60

        result = adapter.response_to_frame(mock_resp)

        assert result.message.content == "我来查一下天气"
        assert len(result.message.tool_calls) == 1
        assert result.message.tool_calls[0].id == "toolu_123"
        assert result.message.tool_calls[0].name == "get_weather"
        assert result.message.tool_calls[0].arguments == {"city": "北京"}

    def test_response_empty_content(self, adapter):
        mock_resp = MagicMock()
        mock_resp.id = "msg_789"
        mock_resp.model = "claude-3"
        mock_resp.content = []
        mock_resp.usage.input_tokens = 10
        mock_resp.usage.output_tokens = 5

        result = adapter.response_to_frame(mock_resp)

        assert result.message.content == ""


class TestAnthropicAdapterInvoke:
    """测试 invoke 和 ainvoke 方法。"""

    def test_invoke_success(self, adapter, llm_request):
        # Mock the client.messages.create method
        with patch.object(adapter.client.messages, "create") as mock_create:
            mock_resp = MagicMock()
            mock_resp.id = "msg_test"
            mock_resp.model = "claude-sonnet-4-20250514"
            mock_resp.content = [MagicMock(type="text", text="Test response")]
            mock_resp.usage.input_tokens = 10
            mock_resp.usage.output_tokens = 5
            mock_create.return_value = mock_resp

            result = adapter.invoke(llm_request)

            assert result.id == "msg_test"
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["model"] == "claude-sonnet-4-20250514"
            assert "max_tokens" in call_kwargs
