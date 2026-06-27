from abc import ABC, abstractmethod
from ..types import LLMResponse, LLMRequest

class ProviderRequest:
    """llm 提供商 的 请求格式"""
    pass

class ProviderResponse:
    """llm 提供商 的 回复格式"""
    pass


class BaseAdapter(ABC):
    @abstractmethod
    def __init__(self, api_key: str = None, base_url: str = None, *args, **kwargs):
        self.api_key = api_key
        self.base_url = base_url


    @abstractmethod
    def invoke(self, llm_request: LLMRequest) -> "LLMResponse":
        pass


