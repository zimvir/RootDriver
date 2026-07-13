from __future__ import annotations
from pydantic import BaseModel, Field




class LLMConfig(BaseModel):
    """LLM 配置。"""

    model_config = {"arbitrary_types_allowed": True}

    adapter: "BaseAdapter"
    """LLM 适配器实例，用户可传入自定义适配器。"""

    model: str
    """模型名称。"""

    temperature: float = 0.7
    max_tokens: int | None = None