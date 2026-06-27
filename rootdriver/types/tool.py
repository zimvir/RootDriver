"""工具相关的数据类型。"""

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """assistant 发起的工具调用。"""

    id: str
    name: str
    arguments: dict = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    """工具定义（发给 LLM）。"""

    name: str
    description: str = ""
    parameters: dict = Field(default_factory=dict)


class ToolRegistry(BaseModel):
    """工具注册表，存多个工具定义。"""

    name: str = ""
    version: str = "1.0.0"
    tools: list[ToolDefinition] = Field(default_factory=list)


class ToolMap(dict):
    """name -> 函数对象 的映射。"""

    def register(self, name: str, func: callable) -> None:
        self[name] = func

    def get_func(self, name: str):
        return self.get(name)


class ToolResult(BaseModel):
    "tool 返回的数据"

    tool_call_id: str
    content:str