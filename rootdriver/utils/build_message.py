
from ..types import Message
from ..utils import get_iso_timestamp
from ..constants import Role


def build_message(
    role: Role,
    content: str | None,
    tool_calls: list | None = None,
    tool_call_id: str = None,
) -> Message:
    if role == Role.USER:
        message = build_user_message(content)
    elif role == Role.SYSTEM:
        message = build_system_message(content)
    elif role == Role.ASSISTANT:
        message = build_assistant_message(content, tool_calls)
    elif role == Role.TOOL:
        message = build_tool_message(tool_call_id, content)
    elif role == Role.I:
        message = build_i_message(content)
    elif role == Role.ENVIRONMENT:
        message = build_environment_message(content)
    elif role == Role.BODY:
        message = build_body_message(content)
    elif role == Role.GENE:
        message = build_gene_message(content)
    else:
        raise ValueError(f"未知角色: {role}")
    return message


def build_system_message(content: str | None) -> Message:
    return Message(role=Role.SYSTEM, content=content, created_at=get_iso_timestamp())


def build_user_message(content: str) -> Message:
    return Message(role=Role.USER, content=content, created_at=get_iso_timestamp())


def build_assistant_message(content: str | None = None, tool_calls: list | None = None) -> Message:
    msg = Message(role=Role.ASSISTANT, content=content, created_at=get_iso_timestamp())
    if tool_calls:
        msg.tool_calls = tool_calls
    return msg


def build_tool_message(tool_call_id: str, content: str) -> Message:
    return Message(
        role=Role.TOOL,
        tool_call_id=tool_call_id,
        content=content,
        created_at=get_iso_timestamp(),
    )


def build_i_message(content: str | None) -> Message:
    return Message(role=Role.I, content=content, created_at=get_iso_timestamp())


def build_environment_message(content: str | None) -> Message:
    return Message(role=Role.ENVIRONMENT, content=content, created_at=get_iso_timestamp())


def build_body_message(content: str | None) -> Message:
    return Message(role=Role.BODY, content=content, created_at=get_iso_timestamp())


def build_gene_message(content: str | None) -> Message:
    return Message(role=Role.GENE, content=content, created_at=get_iso_timestamp())
