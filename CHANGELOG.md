# Changelog

## 0.4.2 (2026-07-05)
-  在 `__init__`.py 不暴露了 `types`、`db`
- 修改了 `pypeoject.toml` 解决了打包时 只打包了顶层包， 不打包子包的问题。

## 0.4.1 (2026-07-04)
- 在 `__init__`.py 暴露了 `types` 



## 0.4.0 (2026-07-04)

### Features

- **JsonDB 模块** - 新增 JSON 文件数据库封装
  - `JsonDB.update()` - 全量覆写指定 checkpoint
  - `JsonDB.append()` - 增量追加单条消息
  - `JsonDB.read()` - 读取 checkpoint 消息列表

- **State 重构** - 持久化模块化，修复多个 bug
  - `State._auto_save()` - 增量自动保存，只追加新消息不全量覆写
  - `State.update_auto_save_data_saved_length()` - 同步已保存长度
  - `auto_save` 参数 - Agent 级别开关，控制是否启用自动保存
  - `Conversation.copy()` - 会话浅拷贝，用于 checkpoint 快照

- **新增异常** - 完善异常体系
  - `StateDBNotFoundError` - 数据库目标对象不存在
  - `DBNotFoundError` - 数据库未找到结果

- **新增工具方法** - `Conversation`
  - `get_message_by_index()` - 按索引获取单条消息
  - `get_message_in_list_by_index()` - 按索引获取消息字典
- **增加两个默认值**
  - `DEFAULT_AGENT_STATE_AUTO_SAVE_NAME`
  - `DEFAULT_AGENT_DB_PATH`
### Bug Fixes

- 修复 `JsonDB.append()` 当 agent 存在但 checkpoint 不存在时的 KeyError
- 修复 `State.save_from_now()` / `save_from_checkpoints()` 未处理 `agent_id=None` 默认值的问题
- 修复 `Conversation` 缺少 `copy()` 方法的问题
- 修复 `Engine` ↔ `Agent` 循环导入问题，改用 `Any` 类型注解

### Code Quality

- 测试覆盖：51 个测试全部通过
- 新增 `tests/test_state.py`，覆盖 JsonDB 和 State 全量功能

---

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