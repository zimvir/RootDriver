__version__ = "0.6.0"
__author__ = "zimvir"
__email__ = "zimvir@qq.com"

from .agent import Agent
from .conversation import Conversation
from .llm import LLM
from .tool import tool, Tool, BaseTool
from .conversation_repo import ConversationRepo
from .exceptions import (
    LLMError,
    LLMInvokeError,
    LLMResponseError,
    ToolError,
    ToolNotFoundError,
    ToolInvokeError,
    ToolArgumentError,
    AgentError,
    ConversationError,
    CheckpointNotFoundError,
    StateDBNotFoundError,
)

__all__ = [
    "Agent",
    "Conversation",
    "LLM",
    "tool",
    "Tool",
    "BaseTool",
    "ConversationRepo",

    "LLMError",
    "LLMInvokeError",
    "LLMResponseError",
    "ToolError",
    "ToolNotFoundError",
    "ToolInvokeError",
    "ToolArgumentError",
    "AgentError",
    "ConversationError",
    "CheckpointNotFoundError",
    "StateDBNotFoundError",
]

from .types.config import LLMConfig
import sys as _sys
LLMConfig.model_rebuild(_types_namespace=_sys.modules['rootdriver.llm'].__dict__)
