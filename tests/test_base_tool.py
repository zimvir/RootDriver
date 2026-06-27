import pytest
from rootdriver.tool.base_tool import BaseTool


def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 晴天"


@pytest.fixture
def weather_tool():
    return BaseTool(get_weather)


def test_base_tool_name(weather_tool):
    assert weather_tool.name == "get_weather"


def test_base_tool_description(weather_tool):
    assert weather_tool.description == "获取城市天气"


def test_invoke_success(weather_tool):
    result = weather_tool.invoke({"city": "北京"})
    assert result == "北京 晴天"


def test_invoke_error_returns_string(weather_tool):
    def bad_func(city: str) -> str:
        raise ValueError("参数错误")
    bad_tool = BaseTool(bad_func)
    result = bad_tool.invoke({"city": "北京"})
    assert isinstance(result, str)
    assert "ValueError" in result or "参数错误" in result


def test_to_definition(weather_tool):
    definition = weather_tool.to_definition()
    assert definition.name == "get_weather"
    assert definition.description == "获取城市天气"
    assert "properties" in definition.parameters
    assert "city" in definition.parameters["properties"]


def test_custom_name():
    def foo():
        pass
    tool = BaseTool(foo, name="custom_name")
    assert tool.name == "custom_name"


def test_custom_description():
    def foo():
        """custom desc"""
        pass
    tool = BaseTool(foo)
    assert tool.description == "custom desc"


def test_callable(weather_tool):
    result = weather_tool(city="上海")
    assert result == "上海 晴天"


def test_invoke_retry_success():
    """retry=1 第一次就成功"""
    call_count = 0
    def counter(city: str) -> str:
        nonlocal call_count
        call_count += 1
        return f"{city} 晴天"
    t = BaseTool(counter)
    result = t.invoke({"city": "北京"}, retry=3)
    assert result == "北京 晴天"
    assert call_count == 1


def test_invoke_retry_then_success():
    """retry=3 前两次失败，第三次成功"""
    call_count = 0
    def flaky(city: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"第{call_count}次失败")
        return f"{city} 晴天"
    t = BaseTool(flaky)
    result = t.invoke({"city": "北京"}, retry=3)
    assert result == "北京 晴天"
    assert call_count == 3


def test_invoke_retry_all_fail():
    """retry=3 三次都失败，返回最后一次错误"""
    call_count = 0
    def always_fail(city: str) -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError(f"错误{call_count}")
    t = BaseTool(always_fail)
    result = t.invoke({"city": "北京"}, retry=3)
    assert "错误3" in result
    assert call_count == 3
