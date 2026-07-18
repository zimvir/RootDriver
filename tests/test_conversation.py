import pytest
from rootdriver.conversation import Conversation
from rootdriver.types import Message
from rootdriver.constants import Role


def test_conversation_empty():
    conv = Conversation()
    assert conv.get_messages() == []


def test_conversation_with_system_prompt():
    conv = Conversation(system_prompt="你是一个助手")
    messages = conv.get_messages()
    assert len(messages) == 1
    assert messages[0].role == Role.SYSTEM
    assert messages[0].content == "你是一个助手"


def test_append_message():
    conv = Conversation()
    conv.append(Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"))
    assert len(conv.get_messages()) == 1
    assert conv.get_messages()[0].content == "你好"


def test_append_many():
    conv = Conversation()
    messages = [
        Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"),
        Message(role=Role.ASSISTANT, content="你好！", created_at="2026-01-01T00:00:01"),
    ]
    conv.append_many(messages)
    assert len(conv.get_messages()) == 2


def test_append_system_message():
    conv = Conversation()
    conv.append_system_message("新的系统提示")
    assert conv.get_messages()[-1].role == Role.SYSTEM
    assert conv.get_messages()[-1].content == "新的系统提示"


def test_delete_message():
    conv = Conversation()
    conv.append(Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"))
    conv.append(Message(role=Role.ASSISTANT, content="你好！", created_at="2026-01-01T00:00:01"))
    conv.remove()
    assert len(conv.get_messages()) == 1


def test_clear():
    conv = Conversation(system_prompt="test")
    conv.clear()
    assert len(conv.get_messages()) == 0


def test_get_messages_in_list():
    conv = Conversation()
    conv.append(Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"))
    result = conv.get_messages_in_list()
    assert isinstance(result, list)
    assert result[0]["content"] == "你好"


def test_from_dict_list():
    data = [
        {"role": "user", "content": "你好", "created_at": "2026-01-01T00:00:00"},
    ]
    conv = Conversation.from_dict_list(data)
    assert len(conv.get_messages()) == 1


def test_from_list():
    messages = [
        Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"),
    ]
    conv = Conversation.from_list(messages)
    assert len(conv.get_messages()) == 1


def test_copy():
    conv = Conversation(system_prompt="原始提示")
    conv.append(Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"))
    copied = conv.copy()

    assert copied.system_prompt == conv.system_prompt
    assert len(copied.get_messages()) == len(conv.get_messages())

    # 修改副本不影响原对象
    copied.append(Message(role=Role.USER, content="新消息", created_at="2026-01-01T00:00:02"))
    assert len(conv.get_messages()) == 2  # 原对象不变
    assert len(copied.get_messages()) == 3  # 副本多了1条


def test_update_message():
    conv = Conversation()
    conv.append(Message(role=Role.USER, content="旧消息", created_at="2026-01-01T00:00:00"))

    new_messages = [
        Message(role=Role.USER, content="新消息1", created_at="2026-01-01T00:00:01"),
        Message(role=Role.ASSISTANT, content="新消息2", created_at="2026-01-01T00:00:02"),
    ]
    conv.update_message(new_messages)

    assert len(conv.get_messages()) == 2
    assert conv.get_messages()[0].content == "新消息1"
    assert conv.get_messages()[1].content == "新消息2"
