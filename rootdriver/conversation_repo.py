from .db import JsonDB
from .conversation import Conversation
from .exceptions import CheckpointNotFoundError, DBAgentIDNotFoundError


class ConversationRepo:
    """Conversation 的持久化仓库。"""

    def __init__(self, db: JsonDB):
        self.db = db

    def save(self, conversation: Conversation, name: str, agent_id: str, start_index:int=0, end_index:int=None) -> None:
        """全量保存 conversation当前数据 到数据库。
        :param end_index: 不填默认最后一个索引
        """
        if end_index is None:
            end_index = len(conversation.messages) - 1
        self.db.update(name, agent_id, conversation.get_messages_in_list()[start_index:end_index])
    def append(self, conversation: Conversation, name: str, agent_id: str, index) -> None:
        message = conversation.get_messages_in_list()[index]
        self.db.append(name, agent_id, message)
    def auto_append(self, conversation: Conversation, name: str, agent_id: str, start_index: int=0) -> None:
        """增量追加，从 start 索引起的 message 追加到数据库。"""
        messages = conversation.get_messages_in_list()
        for i in range(start_index, len(messages)):
            self.db.append(name, agent_id, messages[i])

    def load(self, conversation:Conversation, name: str, agent_id: str) -> Conversation:
        """从数据库加载 conversation，不存在则抛异常。"""
        load_conv = self.get(name, agent_id)
        if load_conv is None:
            load_conv = Conversation.from_messages_list_to_conversation([])
        return conversation.update_message(load_conv.get_messages())

    def get(self, name: str, agent_id: str) -> Conversation | None:
        """从数据库加载 conversation，不存在返回 None。"""
        try:
            messages = self.db.read(name, agent_id)
        except CheckpointNotFoundError:
            return None
        except DBAgentIDNotFoundError:
            return None
        return Conversation.from_dict_list(messages)
