

from .base_adapter import BaseAdapter
from ..types import LLMRequest, LLMResponse

class LLM:

    def __init__(self, adapter:BaseAdapter):
        self.adapter = adapter

    def invoke(self,  llm_request:LLMRequest) -> LLMResponse:
        """
        把信息发给llm， llm返回信息
        Returns:
            LLMResponse
        """

        response = self.adapter.invoke(llm_request)
        return response

    async def ainvoke(self, llm_request: LLMRequest) -> LLMResponse:
        """
        异步把信息发给llm， llm返回信息
        Returns:
            LLMResponse
        """
        response = await self.adapter.ainvoke(llm_request)
        return response

    

