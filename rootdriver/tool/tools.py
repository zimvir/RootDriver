"""工具集合。"""

from typing import Callable
import asyncio
from rootdriver.types.tool import ToolCall, ToolDefinition, ToolResult
from rootdriver.exceptions import ToolNotFoundError

from .base_tool import BaseTool

def tool(func: Callable) -> BaseTool:
    """@tool 装饰器：返回 BaseTool 对象。"""
    return BaseTool(func)


class Tool:
    """工具集合，维护 name -> BaseTool 的映射。"""

    def __init__(self, tools: list[BaseTool] = None) -> None:
        self._map: dict[str, BaseTool] = {}
        if tools:
            for t in tools:
                self._map[t.name] = t

    def add(self, base_tool: BaseTool) -> "Tool":
        """添加一个工具。"""
        self._map[base_tool.name] = base_tool
        return self

    def get(self, name: str) -> BaseTool | None:
        """根据 name 获取工具。"""
        return self._map.get(name)

    def invoke(self, tool_call: ToolCall, *, retry: int = 1) -> ToolResult:
        """执行单个工具调用。"""
        t = self.get(tool_call.name)
        if t is None:
            raise ToolNotFoundError(tool_call.name, list(self._map.keys()))
        content = t.invoke(tool_call.arguments, retry=retry)
        return ToolResult(tool_call_id=tool_call.id, content=content)

    def invoke_many(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        """批量执行工具调用。"""
        return [self.invoke(tc) for tc in tool_calls]

    def to_definitions(self) -> list[ToolDefinition]:
        """生成所有工具的 ToolDefinition 列表（发给 LLM）。"""
        return [t.to_definition() for t in self._map.values()]

    """==========异步部分=========="""

    async def ainvoke(self, tool_call: ToolCall, *, retry: int = 1) -> ToolResult:
        """执行单个工具异步调用。"""
        t = self.get(tool_call.name)
        if t is None:
            raise ToolNotFoundError(tool_call.name, list(self._map.keys()))
        content = await t.ainvoke(tool_call.arguments, retry=retry)
        return ToolResult(tool_call_id=tool_call.id, content=content)

    async def ainvoke_many(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        """批量执行工具调用。"""
        return [await self.ainvoke(tc) for tc in tool_calls]



















