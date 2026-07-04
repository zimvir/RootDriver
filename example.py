"""
RootDriver Agent 记忆持久化示例

演示:
1. Agent 对话并自动保存记忆到 JSON 文件
2. 从 JSON 文件恢复对话历史
3. 手动保存/加载 checkpoint
"""

import os
from rootdriver import Agent
from rootdriver.types.agent import AgentLLM
from rootdriver.llm.adapter.openai_adapter import OpenAIAdapter
from rootdriver.tool.base_tool import BaseTool


def get_weather(city: str) -> str:
    """天气查询工具"""
    return f"{city} 今日晴天，25°C"


# 创建 adapter（需要 OPENAI_API_KEY 环境变量）
adapter = OpenAIAdapter(os.environ.get("MINIMAX_API_KEY"), "https://api.minimaxi.com/v1")
agent_llm = AgentLLM(model="MiniMax-M2.7", adapter=adapter)

# 使用临时文件作为记忆数据库
DB_PATH = "example_db.json"

# ========== 示例1: 正常对话，自动保存 ==========
print("=== 示例1: 对话并自动保存 ===")

agent = Agent(
    agent_llm=agent_llm,
    id="user_001",
    system_prompt="你是一个有用的助手",
    tools=[BaseTool(get_weather)],
    db_path=DB_PATH,
    auto_save=True,
)

# 第一次对话
resp = agent.react("北京天气怎么样？")
print(f"回答: {resp}")

# 对话记录已自动保存到 temp_db
print(f"记忆已保存到: {DB_PATH}\n")

# ========== 示例2: 模拟新会话，从数据库恢复 ==========
print("=== 示例2: 从数据库恢复对话历史 ===")

agent2 = Agent(
    agent_llm=agent_llm,
    id="user_001",  # 同一个 agent_id
    db_path=DB_PATH,
    auto_save=True,
)

# 从数据库加载历史对话
agent2.state.load_from_db("auto_saved")
print(f"恢复消息数: {len(agent2.conversation.get_messages())}")

# 继续对话，历史仍在
resp2 = agent2.react("再说一遍北京天气")
print(f"回答: {resp2}\n")

# ========== 示例3: 手动 checkpoint ==========
print("=== 示例3: 手动 checkpoint ===")

agent3 = Agent(
    agent_llm=agent_llm,
    id="user_002",
    system_prompt="你是一个历史老师",
    db_path=DB_PATH,
)

# 设置检查点（内存快照，不涉及数据库）
agent3.react("唐朝有多少年历史？")
agent3.state.checkpoint("tang_dynasty_backup")
print(f"内存 checkpoint 数: {len(agent3.state.checkpoints)}")

# 保存到数据库
agent3.state.save_from_checkpoints(
    name="tang_history",
    checkpoint_name="tang_dynasty_backup",
)
print(f"已保存 checkpoint 到数据库\n")

# ========== 示例4: 增量追加验证 ==========
print("=== 示例4: 查看保存的 JSON 文件 ===")
with open(DB_PATH, "r", encoding="utf-8") as f:
    import json
    data = json.load(f)
    print(f"数据库中的 agent 列表: {list(data.keys())}")
    for aid, checkpoints in data.items():
        print(f"  {aid}: {list(checkpoints.keys())}")

# 清理
# os.remove(DB_PATH)
print("\n示例完成!")
