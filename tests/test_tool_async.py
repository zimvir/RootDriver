import asyncio
import time
import sys
sys.path.insert(0, "..")

import pytest
from rootdriver.tool import BaseTool, tool

@tool
def sync_weather(city: str) -> str:
    """同步查天气"""
    time.sleep(0.5)
    return f"{city}: 晴天"

@tool
async def async_weather(city: str) -> str:
    """异步查天气"""
    await asyncio.sleep(0.5)
    return f"{city}: 多云"

@pytest.mark.asyncio
async def test_base_tool_ainvoke():
    """测试 BaseTool.ainvoke"""
    result = await sync_weather.ainvoke({"city": "北京"})
    assert "北京" in result and "晴天" in result

    result = await async_weather.ainvoke({"city": "北京"})
    assert "北京" in result and "多云" in result

@pytest.mark.asyncio
async def test_concurrent():
    """测试并发执行"""
    start = time.time()
    results = await asyncio.gather(
        sync_weather.ainvoke({"city": "北京"}),
        sync_weather.ainvoke({"city": "上海"}),
        async_weather.ainvoke({"city": "广州"}),
    )
    elapsed = time.time() - start

    assert elapsed < 0.8, f"应该并发执行，但耗时 {elapsed} 秒"
    assert len(results) == 3

@pytest.mark.asyncio
async def test_ainvoke_many():
    """测试批量异步调用"""
    from rootdriver.types.tool import ToolCall
    from rootdriver.tool import Tool

    tool_calls = [
        ToolCall(id="1", name="sync_weather", arguments={"city": "北京"}),
        ToolCall(id="2", name="async_weather", arguments={"city": "上海"}),
    ]

    tool_set = Tool([sync_weather, async_weather])
    results = await tool_set.ainvoke_many(tool_calls)

    assert len(results) == 2
    assert "北京" in results[0].content
    assert "上海" in results[1].content