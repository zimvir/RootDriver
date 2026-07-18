# Changelog

## 0.7.0 (2026-07-18)

### Features

- **Anthropic 适配器** - 新增 `AnthropicAdapter` (LLMRequest ↔ Anthropic API 格式转换)
  - `request_to_provider()` - LLMRequest 转 Anthropic API 格式
  - `response_to_frame()` - Anthropic API 响应转 LLMResponse
  - `invoke()` / `ainvoke()` - 同步/异步发送请求

- **可选依赖优化** - LLM 适配器作为可选扩展，按需安装
  - `pip install rootdriver[openai]` - 仅 OpenAI 适配器
  - `pip install rootdriver[anthropic]` - 仅 Anthropic 适配器
  - `pip install rootdriver[all]` - 两个都要
  - `pip install rootdriver` - 基础包，无 LLM 适配器

- **可选依赖检测** - 新增 `deal_optional_dependence_installed_status()` 函数
  - 检查指定可选依赖是否已安装
  - 未安装时抛出 `OptionalDependenceNotFoundError`

- **JsonDB 重构** - 分离基类与实现
  - `BaseDB` - 数据库抽象基类
  - `JsonDB` - JSON 文件实现

### Code Quality

- 测试覆盖：63 个测试全部通过
- 新增 `tests/test_anthropic_adapter.py`

## 0.6.1 (2026-07-18)

### Refactor

- **删除 `State` 模块** - 功能已被 `ConversationRepo` 替代，不再需要独立的 State 类
- **清理 `agent.py` 无用 imports** - 移除 `pathlib.Path`、`asyncio`、`State`、`ensure_file_exist`

## 0.6.0 (2026-07-18)

### Breaking Changes

- **`Engine.__init__` 移除 `model` 参数** - `model` 从 Engine 移除，改为由 Agent 在创建时从 `llm_config` 传入
- **`Agent.create()` 替代直接构造** - 推荐使用工厂方法创建 Agent，内部自动组装 LLM、Conversation、Tool、ConversationRepo、Engine
- **`LLM.__init__` 新增 `model` 参数** - 原 `model` 移至 LLM 构造参数
- **`Conversation.append_system` 重命名为 `append_system_message`** - 语义更明确

### Features

- **`ConversationRepo` 重构** - 分离 DBOpt 和 BufferOpt 两个子模块
  - `DBOpt` - 数据库持久化层
    - `update(messages, checkpoint_name)` - 全量覆写
    - `append(message, checkpoint_name)` - 追加单条
    - `sync_append(messages, checkpoint_name, start_index)` - 增量追加
    - `get(checkpoint_name)` - 读取 messages 列表
  - `BufferOpt` - 内存快照层
    - `update(messages, checkpoint_name)` - 保存到内存
    - `get(checkpoint_name)` - 获取 messages
    - `remove(checkpoint_name)` - 删除快照
  - `ConversationRepo.create(db_path, repo_id)` - 工厂方法，自动生成 repo_id
  - `ConversationRepo.open(db_path, repo_id)` - 工厂方法，打开已存在的 repo

- **`LLM` 工具方法**
  - `messages_to_llm_request(messages, tool_definitions)` - 构建 LLM 请求
  - `llm_response_to_message(response)` - 提取响应消息（静态方法）

- **`Agent.create()` 工厂方法** - 简化 Agent 创建流程
  ```python
  agent = Agent.create(
      llm_config=llm_config,
      agent_id="user_001",
      tools=[get_weather],
      system_prompt="你是一个助手",
      db_path="memory.json",
      sync_save=True,
  )
  ```

- **`ensure_json_file()` 新增** - 确保文件存在且为有效 JSON
- **`check_json_format()` 新增** - 检查文件是否为有效 JSON

### Bug Fixes

- 修复 `ensure_json_file()` 判断逻辑反了的问题（有效 JSON 文件被错误清空）
- 修复 `JsonDB.read()` 读取路径错误（`data.get(name)` 应为 `data[agent_id].get(name)`）
- 修复 `JsonDB` 初始化时不检查文件存在性的问题

### Refactor

- **删除 `Engine.create()`** - 工厂方法价值不大，直接使用 `__init__`
- **删除 `State` 与 `Engine` 的循环依赖** - Engine 不再持有 `_agent` 引用
- **`Engine` 持有 `ConversationRepo` 而非 Agent** - 解耦 engine 和 agent
- **`Engine` 内部调用 `LLM` 的静态方法** - `messages_to_llm_request` 和 `llm_response_to_message`
- **`Engine.run()` / `Engine.arun()` 的 sync_save** - 直接调用 `conversation_repo.db_opt.sync_append`
- **`Conversation` 移除 `repo` 属性** - 不再内置 repo，repo 由外部传入
- **`Conversation.copy()` 保留 `system_prompt`** - 修复拷贝丢失 system_prompt 的问题
- **`Conversation.append_system_message`** - 新增，替代原有的 `append_system`
- **测试文件重构** - `test_conversation.py` 和 `test_state.py` 适配新 API

## 0.5.0 (2026-07-12)

### Breaking Changes

- **`AgentLLM` 重命名为 `LLMConfig`** - `types/agent.py` → `types/config.py`，`__init__.py` 导出名 `agent_llm` → `llm_config`，`example.py` 和所有相关引用同步更新
- **`Role` 枚举替换字符串字面量** - `constants.ROLE_ENUM` 元组替换为 `Role(StrEnum)`，所有 role 相关字符串统一使用枚举，OpenAI 适配器需做 `role.value` 转换
- **`JsonDB.read()` 返回值变更** - 不再接受 `raise_error_if_not_found_agent_id` 参数，改为 agent_id 不存在时抛 `DBAgentIDNotFoundError`，checkpoint 不存在时抛 `CheckpointNotFoundError`
- **`Conversation.delete()` 重命名为 `Conversation.remove()`** - 测试文件 `test_conversation.py` 已同步更新

### Features

- **`ConversationRepo` 新增** - Conversation 持久化仓库类，分离持久化逻辑
  - `save(conversation, name, agent_id, start_index, end_index)` - 全量/范围保存 conversation
  - `append(conversation, name, agent_id, index)` - 追加单条消息
  - `auto_append(conversation, name, agent_id, start_index)` - 增量追加从 start_index 起的消息
  - `load(conversation, name, agent_id)` / `get(name, agent_id)` - 加载 conversation

- **`Role` 枚举扩展** - 新增 `I`、`ENVIRONMENT`、`BODY`、`GENE` 角色（用于 Gezheng 项目）
- **`build_message` 扩展** - 新增 `build_i_message`、`build_environment_message`、`build_body_message`、`build_gene_message` 函数
- **`types` 模块新导出** - 新增 `Response`、`Role`、`LLMConfig`、`ToolResult` 到 `types/__init__.py`

### Refactor

- **重命名 `exception.py` → `exceptions.py`** - 符合 Python 复数命名惯例，所有 import 引用已更新
- **`State` 重构** - 内部委托 `ConversationRepo` 处理持久化，删除大量重复代码
  - `State.auto_save_data` 字段名从 `save_length` 改为 `saved_index`
  - `State.save_from_now()`、`_auto_save()`、`get_from_db()`、`load_from_db()` 均已重构
- **删除 `types/messages.py`** - 内容合并到 `types/message.py`
- **`BaseAdapter.__init__` 简化** - 移除强制 `api_key/base_url` 参数，改为 `*args, **kwargs`
- **`__init__.py` 导出精简** - 移除 `BaseAdapter`、`OpenAIAdapter`、`AgentLLM`、`Message`、`ToolDefinition`、`ToolCall`，统一通过 `types` 和 `llm` 子模块访问

### Bug Fixes

- 修复 `State._auto_save()` 字段名不一致问题（`saved_index` vs `save_length`），现统一用 `saved_index`
- 修复 `State.save_from_checkpoints()` 使用了错误的 conversation 源（应使用 `agent.conversation` 而非 `checkpoint`）
- 修复 `State.load_from_db()` 使用了错误的 conversation 源

## 0.4.3 (2026-07-05)
- 修复 `types/__init__.py` 漏暴露 `AgentLLM`、`ToolResult`、`Response` 的问题

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