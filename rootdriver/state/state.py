
from __future__ import annotations
from typing import Any
from ..constants import DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
from ..db import JsonDB
from ..conversation import Conversation
from ..exceptions import CheckpointNotFoundError,StateDBNotFoundError
from ..conversation_repo import ConversationRepo
class State:
    def __init__(self, agent_obj: Any, db_path, auto_save: bool = False):
        self.agent = agent_obj
        self.db = JsonDB(db_path)
        self.checkpoints:dict[str,Conversation] =  {}
        self.auto_save = auto_save
        self.auto_save_data = {"saved_index": 0}
        self.conversation_repo = ConversationRepo(db_path)
    def checkpoint(self, name) -> "State":
        self.checkpoints[name] = self.agent.conversation.copy()
        return self
    def save_from_now(self, name: str, agent_id: str | None = None) -> Agent:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        self.conversation_repo.save(self.agent.conversation, name, agent_id)
        return self.agent


    def _auto_save(self, name: str=DEFAULT_AGENT_STATE_AUTO_SAVE_NAME, agent_id: str | None = None) -> Agent:
        """不是全部覆写，而是计算中间差量之后追加到数据库里"""
        agent_id = agent_id if agent_id is not None else self.agent.id

        self.conversation_repo.auto_append(self.agent.conversation, name, agent_id, self.auto_save_data["saved_index"])
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
        self.conversation_repo.save(self.agent.conversation, name, agent_id)
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
        return self.conversation_repo.get(name, agent_id)

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
        self.conversation_repo.load(self.agent.conversation, name, agent_id)
        return self.agent



    def update_auto_save_data_saved_length(self):
        """获取 len(self.agent.conversation.get_messages()) 更新 self.auto_save["saved_length"]的数值"""
        self.auto_save_data["save_length"] = len(self.agent.conversation.get_messages())