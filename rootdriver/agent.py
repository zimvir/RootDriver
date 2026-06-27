from pathlib import Path
from uuid import uuid4

from .engine import Engine
from .llm import LLM
from .conversation import Conversation
from .tool import Tool, BaseTool
from .types.agent import AgentLLM
from .state import State
from .utils import build_system_message, build_message, build_tool_message, build_user_message, build_assistant_message

class Agent:

    def __init__(
        self,
        agent_llm: AgentLLM,
        id: str | None = None,
        tools: list[BaseTool] | None = None,
        system_prompt: str | None = None,

        db_path: str| None = None,
        # retry: int = 3,
        # timeout: float | None = None,
    ):
        self.id = id if id else uuid4().hex
        self.db_path = db_path

        self.conversation = Conversation(system_prompt)
        self.tool = Tool(tools if tools else [])
        self.state = State(self, self.db_path)

        self.engine = Engine(
            model=agent_llm.model,
            llm=LLM(agent_llm.adapter),
            conversation=self.conversation,
            tool=self.tool,
        )


    def react(self, input_prompt:str) -> "str":
        """一次 react 循环"""
        response = self.engine.run(build_user_message(input_prompt))
        return response.content

    def talk(self, input_prompt:str) -> "str":
        """一次 agent 调用"""
        return self.engine.invoke(build_user_message(input_prompt)).content



