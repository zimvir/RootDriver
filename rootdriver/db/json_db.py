import json

from ..exceptions import DBAgentIDNotFoundError, CheckpointNotFoundError
from pathlib import Path
from ..utils import ensure_json_file
class JsonDB:
    def __init__(self, path):
        self.path = path
        # 确保文件 存在且符合 json 格式
        ensure_json_file(self.path, default_content="{}", use_default_content_if_file_is_empty_str=True)
    def update(self, name: str, agent_id:str, messages: list[dict]) -> "JsonDB":
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
            messages:
        """
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(agent_id) is None:
            data[agent_id] = {}
        data[agent_id][name] = messages
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self

    def append(self, name: str, agent_id, message: dict,) -> "JsonDB":
        """
        Args:
            name: 检查点 的名称
            agent_id: agent的id， 默认当前agent的id
        """
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get(agent_id) is None:
            data[agent_id] = {}
        if data[agent_id].get(name) is None:
            data[agent_id][name] = []
        data[agent_id][name].append(message)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self

    def read(self, name: str, agent_id: str, raise_error_if_not_found:bool=False) -> list[dict]|None:
        """
        Return:
            若 未找到 agent id 报错 DBAgentIDNotFoundError;
            未找到 checpoint 返回 None
        """
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        agent_data = data.get(agent_id)
        if agent_data is None:
            if raise_error_if_not_found is False:
                return []
            else:
                raise DBAgentIDNotFoundError(agent_id, self.path)

        checkpoint  = agent_data.get(name)
        if checkpoint is None:
            if raise_error_if_not_found is False:
                return []
            else:
                raise CheckpointNotFoundError(name, self.path)
        return checkpoint

