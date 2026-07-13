from pathlib import Path
from uuid import uuid4
import asyncio
from .engine import Engine
from .llm import LLM
from .conversation import Conversation
from .tool import Tool, BaseTool
from .types.config import LLMConfig
from .state import State
from .utils import build_user_message, ensure_file_exist
from .constants import DEFAULT_AGENT_DB_PATH

class Agent:

    def __init__(
        self,
        llm_config: LLMConfig,
        id: str | None = None,
        tools: list[BaseTool] | None = None,
        system_prompt: str | None = None,

        db_path: str| None = None,
        auto_save: bool = True,
        # llm_retry: int = 3,
        # timeout: float | None = None,
    ):
        # 检查信息
        ensure_file_exist(db_path,"{}")

        # 初始化模块
        self.id = id if id else uuid4().hex
        self.db_path = DEFAULT_AGENT_DB_PATH
        self.auto_save = auto_save

        self.conversation = Conversation(system_prompt)
        self.tool = Tool(tools if tools else [])
        self.state = State(self, self.db_path, self.auto_save)

        self.engine = Engine(
            model=llm_config.model,
            llm=LLM(llm_config.adapter),
            conversation=self.conversation,
            tool=self.tool,
            _agent=self,
        )
        # 属性初始化
        self.state.update_auto_save_data_saved_length()

    def react(self, input_prompt:str) -> "str":
        """一次 react 循环"""
        response = self.engine.run(build_user_message(input_prompt))
        return response.content

    def talk(self, input_prompt:str) -> "str":
        """一次 agent 调用"""
        return self.engine.invoke(build_user_message(input_prompt)).content


    """==========异步部分=========="""
    async def areact(self, input_prompt:str) -> "str":
        """一次 react 异步循环"""
        response = await self.engine.arun(build_user_message(input_prompt))
        return response.content

    async def atalk(self, input_prompt:str) -> "str":
        """一次 agent 异步调用"""
        return await self.engine.ainvoke(build_user_message(input_prompt)).content



