
from __future__ import annotations

import json

from .llm import LLM
from .conversation import Conversation
from .tool import Tool
from .types import LLMRequest, Message
from .utils import get_iso_timestamp, build_tool_message, build_message, build_user_message
from .conversation_repo import ConversationRepo
from .constants import  DEFAULT_AGENT_DB_PATH, DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
from jsonschema import validate, ValidationError

class Engine:
    def __init__(
            self,
            llm:LLM,
            conversation:Conversation,
            tool:Tool, conversation_repo:ConversationRepo,
            sync_save:bool = False,
            sync_saved_checkpoint_name_in_repo:str = DEFAULT_AGENT_STATE_AUTO_SAVE_NAME
    ):

        self.llm = llm
        self.conversation = conversation
        self.tool = tool
        self.conversation_repo = conversation_repo  # 为实现sync_save
        self.sync_save = sync_save
        self.sync_saved_checkpoint_name = sync_saved_checkpoint_name_in_repo

        
    def invoke(self, input_message:Message) -> Message:
        """但系调用llm，并存入记忆，无tool调用"""
        self.conversation.append(input_message)
        message = self.chat()
        return message

    def chat(self) -> Message:
        """
        1. 读会话消息
        2. 大模型交流
        3. 追加会话消息
        """
        # 1. 读会话消息
        message = self.conversation.get_messages()

        # 2. llm交互
        response = self.llm.invoke(self.llm.messages_to_llm_request(message, self.tool.to_definitions()))

        # 3. 追加会话消息
        response_message = self.llm.llm_response_to_message(response)
        self.conversation.append(response_message)

        return response_message

    def deal_tool_or_output(self, response_message:Message) -> Message|None:
        """
        5. 判断 是否调用工具
        6. 是： tool 返回结果并追加，否： 追加并返回
        """

        # 5. 判断 是否调用工具
        if response_message.tool_calls:
            # 6. 是： tool 返回结果追加
            for tool_call in response_message.tool_calls:
                tool_result = self.tool.invoke(tool_call)
                self.conversation.append(build_tool_message(tool_result.tool_call_id, tool_result.content))
            return None
        else:
            # 6. 否： 追加并返回
            return response_message

    def run(self, input_message:Message) ->Message|None:
        """
        1. 追加输入
        2. 读会话消息
        3. 大模型交流
        4. 追加会话消息
        5. 判断 是否调用工具
        6. 是： tool 返回结果并追加，否： 追加并返回
        Returns:

        """
        self.conversation.append(input_message)
        while True:
            response_message = self.chat()
            result = self.deal_tool_or_output(response_message)
            if result is None:
                continue
            elif isinstance(result, Message):
                if self.sync_save:
                    self.conversation_repo.db_opt.sync(self.conversation.messages, self.sync_saved_checkpoint_name)
                return result

    """==========异步部分=========="""
    async def ainvoke(self, input_message:Message) -> Message:
        """但系调用llm，并存入记忆，无tool调用"""
        self.conversation.append(input_message)
        message = await self.achat()
        return message

    async def achat(self) -> Message:
        """
        1. 读会话消息
        2. 大模型交流
        3. 追加会话消息
        """
        # 1. 读会话消息
        message = self.conversation.get_messages()

        # 2. llm交互
        response = await self.llm.ainvoke(self.llm.messages_to_llm_request(message, self.tool.to_definitions()))

        # 3. 追加会话消息
        response_message = self.llm.llm_response_to_message(response)
        self.conversation.append(response_message)

        return response_message

    async def adeal_tool_or_output(self, response_message:Message) -> Message|None:
        """
        5. 判断 是否调用工具
        6. 是： tool 返回结果并追加，否： 追加并返回
        """

        # 5. 判断 是否调用工具
        if response_message.tool_calls:
            # 6. 是： tool 返回结果追加
            tool_results = await self.tool.ainvoke_many(response_message.tool_calls)
            self.conversation.append_many([build_tool_message(tool_result.tool_call_id, tool_result.content) for tool_result in tool_results])
            return None
        else:
            # 6. 否： 追加并返回
            return response_message

    async def arun(self, input_message:Message) ->Message:
        """
        1. 追加输入
        2. 读会话消息
        3. 大模型交流
        4. 追加会话消息
        5. 判断 是否调用工具
        6. 是： tool 返回结果并追加，否： 追加并返回
        Returns:

        """
        self.conversation.append(input_message)
        while True:
            response_message = await self.achat()
            result = await self.adeal_tool_or_output(response_message)
            if result is None:
                continue
            elif isinstance(result, Message):
                self.conversation_repo.db_opt.sync(
                    self.conversation.messages,
                    self.sync_saved_checkpoint_name
                )
                return result

    '''==========校验=========='''
    def validated_run(self, input_message:Message, schema, retry:int=3) -> Message|None:
        for i in range(retry):
            result_message = self.run(input_message)
            result_json = result_message.content

            try:
                result = json.loads(result_json)
                try:
                    validate(result, schema)
                    return result_message
                except ValidationError as e:
                    input_message = build_user_message(f"数据格式校验未通过:\n{str(e)}")
            except json.decoder.JSONDecodeError as e:
                input_message = build_user_message(f"数据格式 不符合 json 格式。错误:\n{str(e)}")
        return None

    async def avalidated_run(self, input_message: Message, schema, retry: int = 3) -> Message|None:
        for i in range(retry):
            result_message = (await self.arun(input_message))
            result_json = result_message.content
            try:
                result = json.loads(result_json)
                try:
                    validate(result, schema)
                    return result_message
                except ValidationError as e:
                    input_message = build_user_message(f"数据格式校验未通过:\n{str(e)}")
            except json.decoder.JSONDecodeError as e:
                input_message = build_user_message(f"数据格式 不符合 json 格式。错误:\n{str(e)}")
        return None

