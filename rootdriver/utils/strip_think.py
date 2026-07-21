import re


def strip_think_content(text: str) -> str:
    """去除 LLM 返回内容中的 <think>...</think> 思考过程标签及其内容。

    适用于 MiniMax 等把思考过程混在 content 里不遵守规范的服务商。
    """
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
