from abc import ABC, abstractmethod


class BaseDB(ABC):
    """数据库抽象基类，定义统一的持久化接口。"""

    @abstractmethod
    def update(self, name: str, repo_id: str, messages: list[dict]) -> "BaseDB":
        """
        全量覆写指定 agent 的指定 checkpoint。

        Args:
            name: checkpoint 名称
            repo_id: str: agent 唯一标识
            messages: 消息列表（全量覆写）
        """

    @abstractmethod
    def append(self, name: str, repo_id: str, message: dict) -> "BaseDB":
        """
        追加单条消息到指定 agent 的指定 checkpoint。

        Args:
            name: checkpoint 名称
            agent_id: agent 唯一标识
            message: 单条消息字典
        """

    @abstractmethod
    def remove(self, name: str, repo_id: str, index: int = -1) -> "BaseDB":
        """
        删除指定 checkpoint 中的单条消息。

        Args:
            name: checkpoint 名称
            repo_id: agent 唯一标识
            index: 消息索引，默认 -1（最后一条）
        """

    @abstractmethod
    def read(self, name: str, repo_id: str) -> list[dict]:
        """
        读取指定 agent 的指定 checkpoint 的所有消息。

        Args:
            name: checkpoint 名称
            repo_id: agent 唯一标识

        Returns:
            消息列表，不存在时返回空列表
        """
