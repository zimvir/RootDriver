import uuid

from .db import JsonDB, BaseDB
from .types import Message
from .constants import  DEFAULT_AGENT_DB_PATH, DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
class DBOpt:
    """数据库持久化层"""

    def __init__(self, db: BaseDB, repo_id: str):
        self.db = db
        self.repo_id = repo_id

    def update(self, messages:list[Message], checkpoint_name: str) -> 'DBOpt':
        """全量覆写 conversation 到数据库。"""
        self.db.update(
            checkpoint_name,
            self.repo_id,
            [message.model_dump() for message in messages],
        )
        return self

    def append(self, message: Message, checkpoint_name: str) -> "DBOpt":
        """追加单条 message 到数据库。"""
        self.db.append(checkpoint_name, self.repo_id, message.model_dump())
        return self

    def sync(self, messages:list[Message], checkpoint_name: str) -> "DBOpt":
        """同步conv的消息列表到数据库。"""
        self.db.update(checkpoint_name, self.repo_id, [message.model_dump() for message in messages])
        return self
    def remove(self, name:str, index:int=-1) -> "DBOpt":
        self.db.remove(name, self.repo_id, index)
        return self


    def get(self, checkpoint_name: str) -> list[Message]:
        """从数据库返回 messages 列表。"""
        return [Message.model_load(msg_dict) for msg_dict in self.db.read(checkpoint_name, self.repo_id)]


class BufferOpt:
    """内存快照层"""
    def __init__(self):
        self.checkpoints = {}

    def update(self,messages:list[Message],  checkpoint_name: str) -> "BufferOpt":
        """保存 conversation 拷贝到内存快照。"""
        self.checkpoints[checkpoint_name] = messages
        return self

    def get(self, checkpoint_name: str) -> list[Message]|None:
        """从内存快照加载 messages。"""
        messages = self.checkpoints.get(checkpoint_name)
        return messages

    def remove(self, checkpoint_name: str) -> "BufferOpt":
        """删除内存快照。"""
        if checkpoint_name in self.checkpoints:
            del self.checkpoints[checkpoint_name]
        return self


class ConversationRepo:
    """Conversation 的持久化仓库。绑定 conversation/db/repo_id，一对一管理一个 Conversation 的持久化。"""

    def __init__(self, db_opt: DBOpt, buffer_opt: BufferOpt, repo_id: str):
        self.db_opt = db_opt
        self.buffer_opt = buffer_opt
        self.repo_id = repo_id

    @classmethod
    def create(cls, db:BaseDB,  repo_id:str =  None) -> "ConversationRepo":
        """
        :param db
        :param repo_id: 默认会自定生成 uuid4
        :return:
        """
        repo_id = repo_id or str(uuid.uuid4())
        db_opt = DBOpt(db, repo_id)
        buffer_opt = BufferOpt()
        return cls(db_opt, buffer_opt, repo_id)

