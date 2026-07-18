

from .base_adapter import BaseAdapter
from ..types import LLMRequest, LLMResponse, Message


class LLM:

    def __init__(self, adapter: BaseAdapter, model: str):
        self.adapter = adapter
        self.model = model

    def invoke(self, llm_request: LLMRequest) -> LLMResponse:
        """把信息发给 llm，llm 返回信息。"""
        response = self.adapter.invoke(llm_request)
        return response

    async def ainvoke(self, llm_request: LLMRequest) -> LLMResponse:
        """异步把信息发给 llm，llm 返回信息。"""
        response = await self.adapter.ainvoke(llm_request)
        return response

    def messages_to_llm_request(self, messages: list[Message], tool_definitions: list) -> LLMRequest:
        return LLMRequest(
            model=self.model,
            messages=messages,
            tools=tool_definitions,
        )

    @staticmethod
    def llm_response_to_message(response: LLMResponse) -> Message:
        """把 LLM 响应转成 Message 。"""
        return response.message

    

