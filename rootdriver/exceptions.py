"""RootDriver 异常体系。"""


# ============== LLM 相关 ==============

class LLMError(Exception):
    """LLM 调用基类。"""

    def __init__(self, message: str, model: str = None, **kwargs):
        self.model = model
        super().__init__(message)


class LLMInvokeError(LLMError):
    """LLM 调用失败（网络错误、API 错误、超时等）。"""

    def __init__(self, message: str, model: str = None, status_code: int = None, **kwargs):
        self.status_code = status_code
        super().__init__(message, model)


class LLMResponseError(LLMError):
    """LLM 返回格式异常（解析失败、缺少字段等）。"""

    pass


class AdapterError(Exception):
    """适配器基类。"""

    pass


# ============== 工具相关 ==============

class ToolError(Exception):
    """工具基类。"""

    pass


class ToolNotFoundError(ToolError):
    """工具不存在。"""

    def __init__(self, name: str, available: list = None):
        self.name = name
        self.available = available or []
        msg = f"Tool '{name}' not found"
        if available:
            msg += f", available: {available}"
        super().__init__(msg)


class ToolInvokeError(ToolError):
    """工具执行失败。"""

    def __init__(self, name: str, reason: str = None):
        self.name = name
        self.reason = reason
        msg = f"Tool '{name}' invoke failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class ToolArgumentError(ToolError):
    """工具参数错误。"""

    def __init__(self, name: str, missing: list = None, invalid: dict = None):
        self.name = name
        self.missing = missing or []
        self.invalid = invalid or {}
        msg = f"Tool '{name}' argument error"
        if missing:
            msg += f", missing: {missing}"
        super().__init__(msg)


# ============== Agent / 会话相关 ==============

class AgentError(Exception):
    """Agent 基类。"""

    pass


class ConversationError(Exception):
    """会话操作错误。"""

    pass


# ============== State 相关 ==============

class StateError(Exception):
    """State 基类。"""

    pass




class StateSaveError(StateError):
    """状态保存失败。"""


class StateLoadError(StateError):
    """状态加载失败。"""


class StateDBNotFoundError(StateLoadError):
    """数据库目标对象不存在"""


class DBAgentIDNotFoundError(Exception):
    """DB 中 agent_id 不存在"""

    def __init__(self, agent_id: str, db_path: str):
        self.agent_id = agent_id
        self.db_path = db_path
        super().__init__(f"agent_id = {agent_id} 数据库 {db_path} 中不存在")


class CheckpointNotFoundError(Exception):
    """检查点名称不存在"""

    def __init__(self, name: str, db_path: str):
        self.name = name
        self.db_path = db_path
        super().__init__(f"Checkpoint '{name}' ")
# ============= DB 相关 ===============

class DBNotFoundError(Exception):
    """数据库未找到结果"""
