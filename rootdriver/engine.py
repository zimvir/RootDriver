import asyncio

from .llm import LLM
from .conversation import Conversation
from .tool import Tool
from .types import LLMRequest, Message
from .utils import  get_iso_timestamp,build_tool_message, build_message

class Engine:
    def __init__(self, model:str, llm:LLM, conversation:Conversation, tool:Tool, ):
        self.llm = llm
        self.conversation = conversation
        self.tool = tool
        self.model = model

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
        response = self.llm.invoke(self.messages_to_llm_request(message))

        # 3. 追加会话消息
        response_message = self.llm_response_to_message(response)
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


    def run(self, input_message:Message) ->Message:
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
                return result



    

        


    def messages_to_llm_request(self,messages:list[Message]) -> LLMRequest:
        return LLMRequest(
            model=self.model,
            messages=messages,
            tools=self.tool.to_definitions(),
        )

    def llm_response_to_message(self, response) -> Message:
        """把 LLM 响应转成 Message 。"""
        return response.message

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
        response = await self.llm.ainvoke(self.messages_to_llm_request(message))

        # 3. 追加会话消息
        response_message = self.llm_response_to_message(response)
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
                return result
