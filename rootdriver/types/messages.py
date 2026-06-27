"""Message: 对话原子单元（pydantic）

rootdriver 中所有对话、LLM 请求、工具调用的基本数据单元。
"""

from typing import Literal

from pydantic import BaseModel, Field

from .tool import ToolCall
from ..constants import ROLE_ENUM

class Message(BaseModel):
    """一条对话消息。

    同一份 Message 在内部存储、LLM 请求、LLM 响应里都通用。

    content 按 role 的约定：
    - system/user: 文本
    - assistant: 文本或 None（仅工具调用时）
    - tool: 工具返回结果的字符串（通常是 JSON 序列化后的文本）
    """

    # === 必填 ===
    role: Literal[*ROLE_ENUM]
    content: str | None = None
    created_at: str

    # === 可选（按 role 选择性使用）===
    tool_calls: list[ToolCall] = Field(default_factory=list)
    """assistant 时：LLM 决定要调用的工具列表。"""

    tool_call_id: str | None = None
    """tool 时：关联到 assistant 消息里对应 tool_call 的 id。"""

    reasoning: str | None = None
    """assistant 时：思维链 / 推理内容（可选）。"""

    extra: dict = Field(default_factory=dict)
    """扩展点，放任意额外数据。"""


class Usage(BaseModel):
    """LLM token 用量统计。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Response(BaseModel):
    """LLM 返回的整体封装。"""

    id: str
    model: str
    message: Message
    usage: Usage = Field(default_factory=Usage)
    created_at: str
