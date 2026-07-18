"""
RootDriver Agent 记忆持久化示例

演示:
1. Agent 对话并保存记忆到 JSON 文件
2. 从 JSON 文件恢复对话历史
3. 使用 Buffer 内存快照
4. 使用 DBOpt 持久化
"""

import os
from rootdriver import Agent
from rootdriver.types.config import LLMConfig
from rootdriver.llm.adapter.openai_adapter import OpenAIAdapter
from rootdriver.tool.base_tool import BaseTool


def get_weather(city: str) -> str:
    """天气查询工具"""
    return f"{city} 今日晴天，25°C"


# 创建 adapter（需要 API_KEY 环境变量）
adapter = OpenAIAdapter(os.environ.get("MINIMAX_API_KEY"), "https://api.minimaxi.com/v1")
llm_config = LLMConfig(model="MiniMax-M2.7", adapter=adapter)

# 使用临时文件作为记忆数据库
DB_PATH = "example_db.json"


# ========== 示例1: 正常对话，手动保存 ==========
print("=== 示例1: 对话并保存 ===")

agent = Agent.create(
    llm_config=llm_config,
    agent_id="user_001",
    system_prompt="你是一个有用的助手",
    tools=[BaseTool(get_weather)],
    db_path=DB_PATH,
)

# 对话
resp = agent.react("北京天气怎么样？")
print(f"回答: {resp}")

# 手动保存到数据库
agent.conversation_repo.db_opt.update(
    messages=agent.engine.conversation.get_messages(),
    checkpoint_name="session_1"
)
print(f"记忆已保存到: {DB_PATH}\n")


# ========== 示例2: 模拟新会话，从数据库恢复 ==========
print("=== 示例2: 从数据库恢复对话历史 ===")

agent2 = Agent.create(
    llm_config=llm_config,
    agent_id="user_001",  # 同一个 agent_id
    db_path=DB_PATH,
)

# 从数据库加载历史对话
messages = agent2.conversation_repo.db_opt.get("session_1")
agent2.engine.conversation.update_message(messages)
print(f"恢复消息数: {len(agent2.engine.conversation.get_messages())}")

# 继续对话，历史仍在
resp2 = agent2.react("再说一遍北京天气")
print(f"回答: {resp2}\n")


# ========== 示例3: Buffer 内存快照 ==========
print("=== 示例3: Buffer 内存快照 ===")

agent3 = Agent.create(
    llm_config=llm_config,
    agent_id="user_002",
    system_prompt="你是一个历史老师",
    db_path=DB_PATH,
)

# 对话
agent3.react("唐朝有多少年历史？")

# 保存到内存快照（不涉及数据库）
agent3.conversation_repo.buffer_opt.update(
    agent3.engine.conversation.get_messages(),
    "tang_dynasty_backup"
)
print(f"Buffer checkpoint 数: {len(agent3.conversation_repo.buffer_opt.checkpoints)}")

# 从内存快照恢复
restored = agent3.conversation_repo.buffer_opt.get("tang_dynasty_backup")
print(f"从 Buffer 恢复消息数: {len(restored)}\n")


# ========== 示例4: 查看保存的 JSON 文件 ==========
print("=== 示例4: 查看保存的 JSON 文件 ===")
import json
with open(DB_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
    print(f"数据库中的 agent 列表: {list(data.keys())}")
    for aid, checkpoints in data.items():
        print(f"  {aid}: {list(checkpoints.keys())}")

print("\n示例完成!")
