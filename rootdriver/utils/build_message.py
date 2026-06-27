
from ..types import Message
from  ..utils import get_iso_timestamp

def build_message(role: str, content: str | None, tool_calls: list | None = None,
                  tool_call_id: str = None) -> Message:
    if role == "user":
        message = build_user_message(content)
    elif role == "system":
        message = build_system_message(content)
    elif role == "assistant":
        message = build_assistant_message(content, tool_calls)
    elif role == "tool":
        message = build_tool_message(tool_call_id, content)
    else:
        raise ValueError(f'未知角色: {role}')
    return message


def build_system_message(content: str | None) -> Message:
    return Message(role="system", content=content, created_at=get_iso_timestamp())


def build_user_message(content: str) -> "Message":
    return Message(role="user", content=content, created_at=get_iso_timestamp())


def build_assistant_message( content: str | None = None, tool_calls: list | None = None) -> "Message":
    msg = Message(role="assistant", content=content, created_at=get_iso_timestamp())
    if tool_calls:
        msg.tool_calls = tool_calls
    return msg


def build_tool_message(tool_call_id: str, content: str) -> "Message":
    return Message(
        role="tool",
        tool_call_id=tool_call_id,
        content=content,
        created_at=get_iso_timestamp()
    )