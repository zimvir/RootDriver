from uuid import uuid4
from .engine import Engine
from .llm import LLM
from .conversation import Conversation
from .tool import Tool, BaseTool
from .types.config import LLMConfig
from .utils import build_user_message
from .constants import DEFAULT_AGENT_DB_PATH, DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
from .conversation_repo import ConversationRepo

class Agent:
    def __init__(self, id:str, engine:Engine, conversation_repo:ConversationRepo, ):
        self.engine = engine
        self.conversation_repo = conversation_repo
        self.id = id
    @classmethod
    def create(
        cls,
        llm_config: LLMConfig,
        agent_id: str = None,
        tools: list[BaseTool] | None = None,
        system_prompt: str = None,
        db_path: str | None = None,
        sync_save: bool = False,
        sync_saved_checkpoint_name_in_repo: str = DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
    ):
        """
        工厂方法：创建 Agent 实例。

        内部组装：LLM -> Conversation -> Tool -> ConversationRepo -> Engine -> Agent

        Args:
            llm_config: LLM 配置（包含 adapter 和 model）
            agent_id: Agent 唯一标识，默认自动生成 uuid
            tools: 工具列表，默认 None（无工具）
            system_prompt: 系统提示词，默认 None
            db_path: 数据库路径，默认使用 DEFAULT_AGENT_DB_PATH
            sync_save: 是否在每次 run 结束后自动同步保存，默认 False
            sync_saved_checkpoint_name_in_repo: 自动保存的 checkpoint 名称，默认 DEFAULT_AGENT_STATE_AUTO_SAVE_NAME

        Returns:
            Agent 实例
        """
        llm = LLM(llm_config.adapter, llm_config.model)

        if system_prompt:
            conversation = Conversation(system_prompt)
        else:
            conversation = Conversation()

        tool  = Tool(tools)
        agent_id = agent_id or str(uuid4())

        db_path = db_path or DEFAULT_AGENT_DB_PATH
        conversation_repo = ConversationRepo.create(db_path=db_path, repo_id=agent_id)


        engine = Engine(
            llm=llm,
            conversation=conversation,
            tool=tool,
            conversation_repo=conversation_repo,
            sync_save=sync_save,
            sync_saved_checkpoint_name_in_repo=sync_saved_checkpoint_name_in_repo,
        )
        return cls(
            id=agent_id,
            engine=engine,
            conversation_repo=conversation_repo,
        )


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



