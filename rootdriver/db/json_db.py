import json

from ..utils import ensure_json_file
from .base_db import BaseDB


class JsonDB(BaseDB):
    """JSON 文件数据库实现。"""

    def __init__(self, path):
        self.path = path
        # 确保文件存在且符合 json 格式
        ensure_json_file(self.path, default_content="{}", use_default_content_if_file_is_empty_str=True)

    def update(self, name: str, repo_id: str, messages: list[dict]) -> "JsonDB":
        """全量覆写指定 agent 的指定 checkpoint。"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(repo_id) is None:
            data[repo_id] = {}
        data[repo_id][name] = messages
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self

    def append(self, name: str, repo_id: str, message: dict) -> "JsonDB":
        """追加单条消息到指定 agent 的指定 checkpoint。"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(repo_id) is None:
            data[repo_id] = {}
        if data[repo_id].get(name) is None:
            data[repo_id][name] = []
        data[repo_id][name].append(message)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self

    def remove(self, name: str, repo_id: str, index: int = -1) -> "JsonDB":
        """删除指定 checkpoint 中的单条消息。"""
        data = self.read(name, repo_id)
        data.pop(index)
        self.update(name, repo_id, data)
        return self

    def read(self, name: str, repo_id: str) -> list[dict]:
        """读取指定 agent 的指定 checkpoint 的所有消息。"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        agent_data = data.get(repo_id)
        if agent_data is None:
            return []
        checkpoint = agent_data.get(name)
        if checkpoint is None:
            return []
        return checkpoint
