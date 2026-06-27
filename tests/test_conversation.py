import pytest
from rootdriver.conversation import Conversation
from rootdriver.types import Message


def test_conversation_empty():
    conv = Conversation()
    assert conv.get_messages() == []


def test_conversation_with_system_prompt():
    conv = Conversation(system_prompt="你是一个助手")
    messages = conv.get_messages()
    assert len(messages) == 1
    assert messages[0].role == "system"
    assert messages[0].content == "你是一个助手"


def test_append_message():
    conv = Conversation()
    conv.append(Message(role="user", content="你好", created_at="2026-01-01T00:00:00"))
    assert len(conv.get_messages()) == 1
    assert conv.get_messages()[0].content == "你好"


def test_append_many():
    conv = Conversation()
    messages = [
        Message(role="user", content="你好", created_at="2026-01-01T00:00:00"),
        Message(role="assistant", content="你好！", created_at="2026-01-01T00:00:01"),
    ]
    conv.append_many(messages)
    assert len(conv.get_messages()) == 2


def test_append_system():
    conv = Conversation()
    conv.append_system("新的系统提示")
    assert conv.get_messages()[-1].role == "system"
    assert conv.get_messages()[-1].content == "新的系统提示"


def test_delete_message():
    conv = Conversation()
    conv.append(Message(role="user", content="你好", created_at="2026-01-01T00:00:00"))
    conv.append(Message(role="assistant", content="你好！", created_at="2026-01-01T00:00:01"))
    conv.delete()
    assert len(conv.get_messages()) == 1


def test_clear():
    conv = Conversation(system_prompt="test")
    conv.clear()
    assert len(conv.get_messages()) == 0


def test_get_messages_in_list():
    conv = Conversation()
    conv.append(Message(role="user", content="你好", created_at="2026-01-01T00:00:00"))
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
        Message(role="user", content="你好", created_at="2026-01-01T00:00:00"),
    ]
    conv = Conversation.from_list(messages)
    assert len(conv.get_messages()) == 1
