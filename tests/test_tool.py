import pytest
from rootdriver.tool.base_tool import BaseTool
from rootdriver.tool.tools import Tool
from rootdriver.types.tool import ToolCall
from rootdriver.exceptions import ToolNotFoundError


def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 晴天"


def get_time(city: str) -> str:
    """获取城市时间"""
    return f"{city} 10:00"


@pytest.fixture
def weather_tool():
    return BaseTool(get_weather)


@pytest.fixture
def time_tool():
    return BaseTool(get_time)


@pytest.fixture
def tool_registry(weather_tool, time_tool):
    return Tool([weather_tool, time_tool])


def test_tool_add():
    t = Tool()
    t.add(BaseTool(get_weather))
    assert t.get("get_weather") is not None


def test_tool_get(weather_tool):
    t = Tool([weather_tool])
    assert t.get("get_weather") is weather_tool


def test_tool_get_not_found():
    t = Tool()
    assert t.get("not_exist") is None


def test_tool_invoke_success(tool_registry):
    result = tool_registry.invoke(ToolCall(id="1", name="get_weather", arguments={"city": "北京"}))
    assert result.tool_call_id == "1"
    assert result.content == "北京 晴天"


def test_tool_invoke_not_found(tool_registry):
    with pytest.raises(ToolNotFoundError) as exc_info:
        tool_registry.invoke(ToolCall(id="2", name="not_exist", arguments={}))
    assert exc_info.value.name == "not_exist"
    assert "get_weather" in str(exc_info.value.available)


def test_tool_invoke_many(tool_registry):
    calls = [
        ToolCall(id="1", name="get_weather", arguments={"city": "北京"}),
        ToolCall(id="2", name="get_time", arguments={"city": "北京"}),
    ]
    results = tool_registry.invoke_many(calls)
    assert len(results) == 2
    assert results[0].content == "北京 晴天"
    assert results[1].content == "北京 10:00"


def test_tool_to_definitions(tool_registry):
    defs = tool_registry.to_definitions()
    assert len(defs) == 2
    names = [d.name for d in defs]
    assert "get_weather" in names
    assert "get_time" in names
