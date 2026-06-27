

from __future__ import annotations

from .conversation import Conversation
from .exception import CheckpointNotFoundError
import json

class State:
    def __init__(self, agent_obj:Agent, db_path):
        self.agent = agent_obj
        self.db_path = db_path
        self.checkpoints:dict[str,Conversation] =  {}

    def checkpoint(self, name) -> "State":
        self.checkpoints[name] = self.agent.conversation.copy()
        return self
    def save_messages(self, name:str, agent_id, messages:list[dict]) -> Agent:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        # 打开数据库
        data = json.load(self.db_path)
        # 确保有此agent
        if data.get(agent_id) is None:
            data[agent_id] = {}
        data[agent_id][name] = messages
        json.dump(data, self.db_path)
        return self.agent
    def save_from_now(self, name:str, agent_id:str|None=None) -> Agent:
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        self.save_messages(name, agent_id, self.agent.conversation.get_messages_in_list())
        return self.agent
    def save_from_checkpoints(self, name:str,checkpoint_name:str, agent_id:str|None=None) -> Agent:
        """
        Args:
            name: 检查点 的名称
            checkpoint_name : 再checkpoints中的name
            agent_id: agent的id， 默认当前agent的id
        """
        checkpoint = self.checkpoints.get(checkpoint_name)
        if checkpoint is None:
            raise CheckpointNotFoundError(checkpoint_name, "memory")
        messages = checkpoint.get_messages_in_list()
        self.save_messages(name, agent_id, messages)
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
        if agent_id is None:
            agent_id = self.agent.id

        data = json.load(self.db_path)

        if data.get(agent_id) is None:
            raise CheckpointNotFoundError(name, f"db (unknown agent_id: {agent_id})")

        messages = data[agent_id].get(name, None)
        if messages is None:
            raise CheckpointNotFoundError(name, f"db ({self.db_path})")

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
