from typing import Callable

from ..types.tool import ToolDefinition

class BaseTool:
    """工具对象，封装函数 + 元数据。"""

    def __init__(self, func: Callable, name: str = None, description: str = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip()

    def invoke(self, arguments: dict, *, retry: int = 1) -> str:
        """执行工具，返回字符串。retry: 失败重试次数。"""
        last_error = None
        for _ in range(retry):
            try:
                return str(self.func(**arguments))
            except Exception as e:
                last_error = e
        return str(last_error)

    def to_definition(self) -> ToolDefinition:
        """生成发给 LLM 的 ToolDefinition。"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self._generate_parameters(),
        )

    def _generate_parameters(self) -> dict:
        """从函数签名生成 parameters JSON Schema。"""
        import inspect

        sig = inspect.signature(self.func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = param.annotation.__name__ if param.annotation is not inspect.Parameter.empty else "string"
            prop = {"type": param_type}

            if param.default is not inspect.Parameter.empty:
                prop["default"] = param.default
            else:
                parameters["required"].append(param_name)

            parameters["properties"][param_name] = prop

        return parameters

    def __call__(self, **kwargs):
        return self.invoke(kwargs)

