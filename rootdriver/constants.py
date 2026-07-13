
from enum import StrEnum


class Role(StrEnum):
    """对话角色枚举。


    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    # 以下是 Gezheng 项目的角色枚举， 除了这些，它还用了 tool
    I = "i"
    ENVIRONMENT = "environment"
    BODY = "body"
    GENE  = "gene"


DEFAULT_AGENT_STATE_AUTO_SAVE_NAME = "auto_saved"
DEFAULT_AGENT_DB_PATH = "conversations.json"