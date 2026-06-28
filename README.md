# RootDriver

根源出发，驱动万物

一个轻量级的 Python AI Agent 开发框架，支持单智能体和多智能体应用。

## 特性

- **简洁易用**：装饰器方式定义工具，快速构建 Agent
- **模块化设计**：LLM 适配器、工具系统、会话管理解耦
- **工具调用**：支持 function calling，自动执行工具并返回结果
- **状态管理**：支持内存和数据库持久化检查点
- **异常体系**：完整的异常类层次结构
- **异步支持**：全面异步支持，并发多 Agent / 工具调用

## 安装

```bash
pip install rootdriver
```

## 快速开始

### 定义工具

```python
from rootdriver import tool

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city} 晴天"
```

### 创建 Agent

```python
from rootdriver import Agent, AgentLLM, OpenAIAdapter

agent_llm = AgentLLM(
    adapter=OpenAIAdapter(
        api_key="YOUR_API_KEY",
        base_url="BASE_URL"
    ),
    model= "gpt-4",
    temperature=0.7
    )


agent = Agent(
    agent_llm=agent_llm,
    tools=[get_weather],
    system_prompt="你是一个有用的助手",
)

# 单次对话(无 tool)
response = agent.talk("北京天气怎么样？")
print(response)
```

### 使用工具

```python
# 完整对话循环（包含工具调用）
response = agent.react("帮我查下上海天气")
print(response)
```

### 异步用法

```python
import asyncio
from rootdriver import Agent, AgentLLM, OpenAIAdapter

async def main():

    # 单次异步对话
    response = await agent.atalk("你好")
    print(response)

    # 并发多个 Agent
    results = await asyncio.gather(
        agent.areact("问题1"),
        agent.areact("问题2"),
        agent.areact("问题3"),
    )

asyncio.run(main())
```

## 核心组件

| 组件 | 说明 |
|------|------|
| `Agent` | 智能体入口，整合 LLM、工具、会话 |
| `Engine` | 核心引擎，处理对话循环和工具调用 |
| `Conversation` | 会话管理，维护消息历史 |
| `LLM` | LLM 调用封装 |
| `Tool` | 工具集合，管理所有可调用工具 |
| `State` | 状态管理，支持检查点和持久化 |

## 项目结构

```
rootdriver/
├── agent.py           # Agent 智能体
├── engine.py          # 引擎核心
├── conversation.py    # 对话管理
├── state.py           # 状态管理
├── exception.py       # 异常定义
├── llm/
│   ├── llm.py         # LLM 封装
│   ├── base_adapter.py    # 适配器基类
│   └── adapter/
│       └── openai_adapter.py  # OpenAI 适配器
├── tool/
│   ├── base_tool.py   # 工具基类
│   └── tools.py       # 工具集
├── types/             # 类型定义
└── utils/             # 工具函数
```

## License

MIT