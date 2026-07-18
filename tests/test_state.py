import pytest
import json
import tempfile
import os

from rootdriver.db import JsonDB
from rootdriver.conversation import Conversation
from rootdriver.conversation_repo import ConversationRepo, DBOpt, BufferOpt
from rootdriver.types import Message
from rootdriver.constants import Role
from rootdriver.exceptions import CheckpointNotFoundError


@pytest.fixture
def temp_db_path():
    """创建临时数据库文件"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def conversation():
    """创建带消息的 conversation"""
    conv = Conversation(system_prompt="你是一个助手")
    conv.append(Message(role=Role.USER, content="你好", created_at="2026-01-01T00:00:00"))
    conv.append(Message(role=Role.ASSISTANT, content="你好！", created_at="2026-01-01T00:00:01"))
    return conv


class TestJsonDB:
    """JsonDB 单元测试"""

    def test_update_creates_checkpoint(self, temp_db_path):
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

    def test_read_returns_messages(self, temp_db_path):
        db = JsonDB(temp_db_path)
        messages = [{"role": "user", "content": "你好"}]
        db.update("checkpoint1", "agent1", messages)

        result = db.read("checkpoint1", "agent1")
        assert result == messages

    def test_read_returns_empty_when_not_found(self, temp_db_path):
        db = JsonDB(temp_db_path)
        result = db.read("nonexistent", "agent1")
        assert result == []


class TestDBOpt:
    """DBOpt 单元测试"""

    def test_update_full_overwrite(self, temp_db_path, conversation):
        db = JsonDB(temp_db_path)
        db_opt = DBOpt(db, "agent1")

        db_opt.update(conversation.get_messages(), "session_1")

        with open(temp_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "session_1" in data["agent1"]
        assert len(data["agent1"]["session_1"]) == 3  # system + user + assistant

    def test_append_single_message(self, temp_db_path, conversation):
        db = JsonDB(temp_db_path)
        db_opt = DBOpt(db, "agent1")

        db_opt.update(conversation.get_messages(), "session_1")
        new_msg = Message(role=Role.USER, content="新消息", created_at="2026-01-01T00:00:02")
        db_opt.append(new_msg, "session_1")

        result = db_opt.get("session_1")
        assert len(result) == 4

    def test_sync_append_incremental(self, temp_db_path, conversation):
        db = JsonDB(temp_db_path)
        db_opt = DBOpt(db, "agent1")

        # 先保存前2条
        db_opt.update(conversation.get_messages()[:2], "session_1")

        # 增量追加剩余消息
        db_opt.sync_append(conversation.get_messages(), "session_1", start_index=2)

        result = db_opt.get("session_1")
        assert len(result) == 3

    def test_get_returns_messages(self, temp_db_path, conversation):
        db = JsonDB(temp_db_path)
        db_opt = DBOpt(db, "agent1")

        db_opt.update(conversation.get_messages(), "session_1")

        result = db_opt.get("session_1")
        assert len(result) == 3
        assert isinstance(result[0], Message)


class TestBufferOpt:
    """BufferOpt 内存快照测试"""

    def test_update_saves_copy(self, conversation):
        buffer = BufferOpt()

        buffer.update(conversation.get_messages(), "backup_1")

        assert "backup_1" in buffer.checkpoints
        assert len(buffer.checkpoints["backup_1"]) == 3

    def test_get_returns_messages(self, conversation):
        buffer = BufferOpt()
        buffer.update(conversation.get_messages(), "backup_1")

        result = buffer.get("backup_1")
        assert result == conversation.get_messages()

    def test_get_returns_none_when_not_found(self):
        buffer = BufferOpt()
        result = buffer.get("nonexistent")
        assert result is None

    def test_remove_deletes_checkpoint(self, conversation):
        buffer = BufferOpt()
        buffer.update(conversation.get_messages(), "backup_1")
        buffer.remove("backup_1")

        assert "backup_1" not in buffer.checkpoints


class TestConversationRepo:
    """ConversationRepo 集成测试"""

    def test_create_generates_repo_id(self, temp_db_path):
        repo = ConversationRepo.create(JsonDB(temp_db_path))
        assert repo.repo_id is not None

    def test_create_with_custom_repo_id(self, temp_db_path):
        repo = ConversationRepo.create(JsonDB(temp_db_path), repo_id="my_agent")
        assert repo.repo_id == "my_agent"

    def test_db_opt_update(self, temp_db_path, conversation):
        repo = ConversationRepo.create(JsonDB(temp_db_path), repo_id="agent1")
        repo.db_opt.update(conversation.get_messages(), "session_1")

        result = repo.db_opt.get("session_1")
        assert len(result) == 3

    def test_buffer_opt_update(self, temp_db_path, conversation):
        repo = ConversationRepo.create(JsonDB(temp_db_path), repo_id="agent1")
        repo.buffer_opt.update(conversation.get_messages(), "backup_1")

        result = repo.buffer_opt.get("backup_1")
        assert result == conversation.get_messages()

    def test_open_existing_repo(self, temp_db_path, conversation):
        # 创建并保存
        repo1 = ConversationRepo.create(JsonDB(temp_db_path), repo_id="agent1")
        repo1.db_opt.update(conversation.get_messages(), "session_1")

        # 用相同 repo_id 重新创建（open 的替代方案）
        repo2 = ConversationRepo.create(JsonDB(temp_db_path), repo_id="agent1")
        result = repo2.db_opt.get("session_1")
        assert len(result) == 3
