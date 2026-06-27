from pydantic import BaseModel, Field

from .messages import Message
from .tool import ToolDefinition





class LLMRequest(BaseModel):
    """LLM 请求的内部统一格式。"""

    model: str
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int | None = None
    tools: list[ToolDefinition] = Field(default_factory=list)


class Usage(BaseModel):
    """LLM token 用量统计。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    """LLM 返回的整体封装。"""

    id: str
    model: str
    message: "Message"
    usage: Usage = Field(default_factory=Usage)
    created_at: str