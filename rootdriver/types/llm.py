from pydantic import BaseModel, Field

from .message import Message
from .tool import ToolDefinition





class LLMRequest(BaseModel):
    """LLM 请求的内部统一格式。"""

    model: str
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int | None = None   # 这个属性在这个框架里没太大用，但openai 库里要，总之不要改
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