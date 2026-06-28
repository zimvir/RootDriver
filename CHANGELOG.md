# Changelog

## 0.3.0 (2026-06-28)

### Features

- **异步支持** - 全面支持异步操作，支持并发多 Agent 场景
  - `BaseTool.ainvoke()` - 异步工具执行
  - `Tool.ainvoke()` / `Tool.ainvoke_many()` - 异步工具调用
  - `OpenAIAdapter.ainvoke()` - 异步 LLM 调用
  - `LLM.ainvoke()` - 异步 LLM 封装
  - `Engine.ainvoke()` / `Engine.achat()` / `Engine.arun()` - 异步引擎
  - `Agent.areact()` / `Agent.atalk()` - 异步 Agent

- **并发优化** - 同步函数自动转异步执行
  - 使用 `asyncio.to_thread()` 避免同步工具阻塞事件循环
  - 支持 `asyncio.gather()` 并发执行多个工具/Agent

### Code Quality

- 测试覆盖：31 个测试全部通过
- 新增异步工具测试 `test_tool_async.py`

---

## 0.2.0 (2026-06-27)

### Features

- **State 模块** - 新增状态管理，支持内存和数据库持久化检查点
  - `checkpoint()` - 内存快照
  - `save_from_now()` / `save_from_checkpoints()` - 持久化到数据库
  - `load_from_checkpoint()` / `load_from_db()` - 恢复状态

- **异常体系** - 完整的异常类层次结构
  - `LLMError` / `LLMInvokeError` / `LLMResponseError` - LLM 相关
  - `ToolError` / `ToolNotFoundError` / `ToolInvokeError` - 工具相关
  - `StateError` / `CheckpointNotFoundError` - 状态相关

### Bug Fixes

- 修复循环导入问题（`state.py` ↔ `agent.py`）
- 修复 `State.save_messages()` 未写回数据库的问题
- 修复 `State.get_from_db()` 返回类型错误

### Code Quality

- 测试覆盖：28 个测试全部通过

---

## 0.1.0 (2026-06-27)

### Migration from RootEngine

**原因：**
PyPI 包名冲突。`rootengine-core` 已发布在 PyPI 上，导致无法再发布 `rootengine` 包（PyPI 判定名字太相似）。在 GitHub 提交了 issue #541，但处理队列正在处理到 2025 年的（当前2026中旬），等不起。

**迁移详情：**
- 项目从 `RootEngine` 复制到 `RootDriver`
- 所有 `rootengine` 内部引用已替换为 `rootdriver`
- 包结构完整保留，未做任何功能修改

**复制内容：**
```
rootdriver/
├── __init__.py
├── agent.py           # Agent 智能体
├── engine.py          # 引擎核心
├── conversation.py    # 对话管理
├── constants.py       # 常量定义
├── exception.py       # 异常
├── llm/
│   ├── __init__.py
│   ├── llm.py         # LLM 封装
│   ├── base_adapter.py    # 适配器基类
│   └── adapter/
│       ├── __init__.py
│       └── openai_adapter.py  # OpenAI 适配器
├── tool/
│   ├── __init__.py
│   ├── base_tool.py   # 工具基类
│   └── tools.py       # 工具集
├── types/
│   ├── __init__.py
│   ├── agent.py       # Agent 类型
│   ├── llm.py         # LLM 类型
│   ├── messages.py    # 消息类型
│   └── tool.py        # 工具类型
└── utils/
    ├── __init__.py
    ├── build_message.py  # 消息构建
    └── time.py        # 时间工具

tests/
├── __init__.py
├── test_base_tool.py
├── test_conversation.py
└── test_tool.py
```

**版本说明：**
- 版本号从 0.1.0 重新开始（独立于 RootEngine）
- 功能与 RootEngine 最后版本完全一致