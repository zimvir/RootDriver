
from __future__ import annotations
from typing import Any
from ..constants import DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
from ..db import JsonDB
from ..conversation import Conversation
from ..exception import CheckpointNotFoundError,StateDBNotFoundError
import json

class State:
    def __init__(self, agent_obj: Any, db_path, auto_save: bool = False):
        self.agent = agent_obj
        self.db = JsonDB(db_path)
        self.checkpoints:dict[str,Conversation] =  {}
        self.auto_save = auto_save
        self.auto_save_data = {"save_length": 0}
    def checkpoint(self, name) -> "State":
        self.checkpoints[name] = self.agent.conversation.copy()
        return self
    def save_from_now(self, name: str, agent_id: str | None = None) -> Agent:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        agent_id = agent_id if agent_id is not None else self.agent.id
        self.db.update(name, agent_id, self.agent.conversation.get_messages_in_list())
        return self.agent


    def _auto_save(self, name: str=DEFAULT_AGENT_STATE_AUTO_SAVE_NAME, agent_id: str | None = None) -> Agent:
        """不是全部覆写，而是计算中间差量之后追加到数据库里"""
        agent_id = agent_id if agent_id is not None else self.agent.id

        current_len = len(self.agent.conversation.get_messages())
        saved_len = self.auto_save_data["save_length"]

        if current_len <= saved_len:
            return self.agent
        messages = self.agent.conversation.get_messages_in_list()

        for i in range(saved_len, current_len):
            self.db.append(name, agent_id, messages[i])
        self.auto_save_data["save_length"] = current_len
        return self.agent

    def save_from_checkpoints(self, name: str, checkpoint_name: str, agent_id: str | None = None) -> Agent:
        """
        Args:
            name: 检查点 的名称
            checkpoint_name : 再checkpoints中的name
            agent_id: agent的id， 默认当前agent的id
        """
        agent_id = agent_id if agent_id is not None else self.agent.id
        checkpoint = self.checkpoints.get(checkpoint_name)
        if checkpoint is None:
            raise CheckpointNotFoundError(checkpoint_name, "memory")
        messages = checkpoint.get_messages_in_list()
        self.db.update(name, agent_id, messages)
        return self.agent

    def get_from_checkpoints(self, name) -> Conversation:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        Return:
            Conversation
        """

        checkpoint:Conversation = self.checkpoints.get(name, None)
        if checkpoint is None:
            raise CheckpointNotFoundError(name, "memory")
        return checkpoint
    def get_from_db(self, name, agent_id:str|None=None) -> Conversation:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        Return:
            Conversation
        """
        agent_id = agent_id if agent_id is not None else self.agent.id
        try:
            messages = self.db.read(name, agent_id, raise_error_if_not_found_agent_id=True)
            if messages is None:
                raise CheckpointNotFoundError(name, f"db ({self.db_path})")
        except StateDBNotFoundError:
            raise StateDBNotFoundError(f'agent_id = {agent_id} 数据库 {self.db.path} 中不存在')

        return Conversation.from_messages_list_to_conversation(messages)

    def load_from_checkpoint(self, name:str|None=None) -> Agent:
        messages = self.get_from_checkpoints(name).messages
        self.agent.conversation.update_message(messages)
        return self.agent

    def load_from_db(self, name:str|None=None, agent_id:str|None =None ) -> Agent:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        agent_id = agent_id if agent_id is not None else self.agent.id
        messages = self.get_from_db(name, agent_id).messages
        self.agent.conversation.update_message(messages)
        return self.agent

    def update_auto_save_data_saved_length(self):
        """获取 len(self.agent.conversation.get_messages()) 更新 self.auto_save["saved_length"]的数值"""
        self.auto_save_data["save_length"] = len(self.agent.conversation.get_messages())