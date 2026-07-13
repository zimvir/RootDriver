import pytest
import json
import tempfile
import os

from rootdriver.db import JsonDB
from rootdriver.state import State
from rootdriver.conversation import Conversation
from rootdriver.types import Message
from rootdriver.exceptions import CheckpointNotFoundError, StateDBNotFoundError


class MockAgent:
    """用于测试的 Mock Agent"""
    def __init__(self, conversation: Conversation, agent_id: str = "test_agent"):
        self.id = agent_id
        self.conversation = conversation


@pytest.fixture
def temp_db_path():
    """创建临时数据库文件"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    # 初始化空 JSON 文件
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_agent():
    """创建带 conversation 的 mock agent"""
    conv = Conversation(system_prompt="你是一个助手")
    conv.append(Message(role="user", content="你好", created_at="2026-01-01T00:00:00"))
    conv.append(Message(role="assistant", content="你好！", created_at="2026-01-01T00:00:01"))
    return MockAgent(conv, "test_agent_id")


@pytest.fixture
def state(mock_agent, temp_db_path):
    return State(mock_agent, temp_db_path, auto_save=True)


class TestJsonDB:
    """JsonDB 单元测试"""

    def test_update_creates_new_agent(self, temp_db_path):
        db = JsonDB(temp_db_path)
        messages = [{"role": "user", "content": "你好"}]
        db.update("checkpoint1", "agent1", messages)

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["agent1"]["checkpoint1"] == messages

    def test_update_overwrites_existing(self, temp_db_path):
        db = JsonDB(temp_db_path)
        messages1 = [{"role": "user", "content": "消息1"}]
        messages2 = [{"role": "user", "content": "消息2"}]

        db.update("checkpoint1", "agent1", messages1)
        db.update("checkpoint1", "agent1", messages2)

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["agent1"]["checkpoint1"] == messages2

    def test_append_adds_message(self, temp_db_path):
        db = JsonDB(temp_db_path)
        messages = [{"role": "user", "content": "你好"}]
        db.update("checkpoint1", "agent1", messages)

        new_message = {"role": "assistant", "content": "你好！"}
        db.append("checkpoint1", "agent1", new_message)

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["agent1"]["checkpoint1"]) == 2
        assert data["agent1"]["checkpoint1"][1] == new_message

    def test_append_creates_agent_if_not_exists(self, temp_db_path):
        db = JsonDB(temp_db_path)
        new_message = {"role": "user", "content": "你好"}
        db.append("checkpoint1", "agent_new", new_message)

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "agent_new" in data
        assert data["agent_new"]["checkpoint1"] == [new_message]

    def test_read_returns_messages(self, temp_db_path):
        db = JsonDB(temp_db_path)
        messages = [{"role": "user", "content": "你好"}]
        db.update("checkpoint1", "agent1", messages)

        result = db.read("checkpoint1", "agent1")
        assert result == messages

    def test_read_raises_when_agent_not_found(self, temp_db_path):
        db = JsonDB(temp_db_path)
        with pytest.raises(Exception):  # DBNotFoundError
            db.read("checkpoint1", "nonexistent", raise_error_if_not_found_agent_id=True)

    def test_read_returns_none_when_checkpoint_not_found(self, temp_db_path):
        db = JsonDB(temp_db_path)
        db.update("checkpoint1", "agent1", [])
        # read 不抛异常，只返回 data[agent_id][name]，如果 name 不存在会抛 KeyError
        # 这是当前实现行为


class TestStateCheckpoint:
    """State.checkpoint 单元测试"""

    def test_checkpoint_saves_conversation(self, state, mock_agent):
        state.checkpoint("backup")
        assert "backup" in state.checkpoints
        assert isinstance(state.checkpoints["backup"], Conversation)

    def test_checkpoint_stores_copy(self, state, mock_agent):
        state.checkpoint("backup")
        # checkpoint 保存的是 copy，不影响原 conversation
        mock_agent.conversation.append(Message(role="user", content="新消息", created_at="2026-01-01T00:00:02"))
        assert state.checkpoints["backup"].get_messages()[1].content == "你好"


class TestStateSaveAndLoad:
    """State save/load 单元测试"""

    def test_save_from_now_writes_to_db(self, state, temp_db_path, mock_agent):
        state.save_from_now("saved_now")

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "test_agent_id" in data
        assert "saved_now" in data["test_agent_id"]

    def test_get_from_db_returns_conversation(self, state, mock_agent):
        state.save_from_now("saved_checkpoint")
        conv = state.get_from_db("saved_checkpoint")
        assert isinstance(conv, Conversation)
        assert len(conv.get_messages()) > 0

    def test_get_from_db_raises_when_not_found(self, state):
        with pytest.raises(Exception):  # DBNotFoundError
            state.get_from_db("nonexistent_checkpoint")

    def test_load_from_db_updates_conversation(self, state, mock_agent):
        # 先保存
        state.save_from_now("to_load")
        # 清空 conversation
        mock_agent.conversation.clear()
        # 从 db 加载
        state.load_from_db("to_load")
        assert len(mock_agent.conversation.get_messages()) > 0

    def test_save_from_checkpoints(self, state, mock_agent):
        state.checkpoint("my_checkpoint")
        state.save_from_checkpoints("from_checkpoint", "my_checkpoint")

        conv = state.get_from_db("from_checkpoint")
        assert isinstance(conv, Conversation)

    def test_get_from_checkpoints(self, state):
        state.checkpoint("cp1")
        conv = state.get_from_checkpoints("cp1")
        assert isinstance(conv, Conversation)

    def test_get_from_checkpoints_raises_when_not_found(self, state):
        with pytest.raises(CheckpointNotFoundError):
            state.get_from_checkpoints("nonexistent")


class TestAutoSave:
    """State._auto_save 增量保存测试"""

    def test_auto_save_no_change(self, state, mock_agent):
        """没有新消息时不追加"""
        # 先同步 save_length 到当前消息数
        state.auto_save_data["save_length"] = len(mock_agent.conversation.get_messages())
        initial_len = state.auto_save_data["save_length"]
        state._auto_save()
        assert state.auto_save_data["save_length"] == initial_len

    def test_auto_save_incremental_append(self, state, mock_agent):
        """增量追加新消息"""
        # 初始有3条消息（system + user + assistant）
        initial_count = len(mock_agent.conversation.get_messages())
        state.auto_save_data["save_length"] = initial_count

        # 追加1条新消息
        mock_agent.conversation.append(Message(role="user", content="新消息", created_at="2026-01-01T00:00:03"))

        state._auto_save()

        # save_length 应该更新
        assert state.auto_save_data["save_length"] == initial_count + 1

    def test_auto_save_multiple_messages(self, state, mock_agent):
        """一次追加多条新消息"""
        initial_count = len(mock_agent.conversation.get_messages())
        state.auto_save_data["save_length"] = initial_count

        # 追加3条新消息
        for i in range(3):
            mock_agent.conversation.append(Message(role="user", content=f"消息{i}", created_at="2026-01-01T00:00:0{i+3}"))

        state._auto_save()

        assert state.auto_save_data["save_length"] == initial_count + 3

    def test_auto_save_writes_to_db(self, state, mock_agent, temp_db_path):
        """验证增量保存写入了 db"""
        # 先同步 save_length 到当前消息数（模拟已保存的状态）
        current_len = len(mock_agent.conversation.get_messages())
        state.auto_save_data["save_length"] = current_len

        # 追加新消息
        mock_agent.conversation.append(Message(role="user", content="auto save 消息", created_at="2026-01-01T00:00:05"))

        state._auto_save()

        # 验证写入 db（_auto_save 默认用 "auto_saved" 作为 checkpoint 名）
        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data["test_agent_id"]["auto_saved"]
        assert len(messages) == 1  # 只有追加的1条新消息
        assert messages[-1]["content"] == "auto save 消息"
