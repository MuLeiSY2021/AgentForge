# AgentForge

**自生长的多智能体编排系统。**

跟现有框架（CrewAI、AutoGen）不同，它们需要开发者手动定义 Agent 和工作流。AgentForge 有一个 Agent 池和 Group 池，用户提出需求后，系统通过 RAG 自动匹配最合适的 AgentGroup；如果没有合适的，系统会自动规划并创建新的 Agent 和工作流，执行完后存入池中供未来复用。系统会越用越聪明。

## 核心特性

- **自动匹配** — 通过 RAG 向量检索，从池中找到最合适的 Agent 组合
- **自动创建** — 没有合适的？LLM 自动规划并创建新的 Agent 和工作流
- **越用越聪明** — 执行过的工作流存入池中，下次直接复用
- **质量监督** — SupervisorAgent 自动审查执行结果
- **CLI 优先** — 命令行直接操作，未来可扩展 Web UI

## 快速开始

### 安装

```bash
cd agent_forge
pip install -e ".[dev]"
```

### 配置

复制环境变量模板并填入你的 OpenAI API Key：

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

### 使用

```bash
# 查看帮助
agent-forge --help

# 管理 Agent
agent-forge agent list
agent-forge agent add "researcher" --role "信息检索专家"

# 管理 Group
agent-forge group list

# 查看可用工具
agent-forge tool list

# 提交需求（需要有效的 OpenAI API Key）
agent-forge run request "帮我调研 Python Web 框架的优缺点"
```

也可以通过模块方式运行：

```bash
python -m agent_forge --help
```

## 项目结构

```
src/agent_forge/
├── config/          # pydantic-settings 配置
├── models/          # 数据模型（Agent, Group, Workflow, Tool, Execution）
├── llm/             # async OpenAI 客户端封装
├── storage/         # 持久化存储（抽象接口 + JSON 文件实现）
├── pool/            # Agent 池 / Group 池 CRUD
├── tools/           # 工具系统（BaseTool + Registry + 内置工具）
├── rag/             # 向量检索（OpenAI embedding + 余弦相似度）
├── engine/          # RuntimeContext 组合根 + WorkflowExecutor
├── agents/          # MetaAgent（系统大脑）+ SupervisorAgent（监督）
├── cli/             # Typer CLI
└── utils/           # 日志等工具
```

## 架构设计

| 决策 | 理由 |
|---|---|
| src layout | 防止意外导入，便于未来添加 web 包 |
| 全异步 | OpenAI SDK 原生 async，CLI 用 `asyncio.run()` 桥接 |
| RuntimeContext 组合根 | 手动依赖注入，显式清晰，无框架魔法 |
| numpy 做 RAG | 初期规模小，避免 chromadb 重依赖 |
| ToolSpec 与 BaseTool 分离 | 序列化元数据与可执行代码解耦 |

## 开发

```bash
# 运行测试
pytest tests/

# 代码检查
ruff check src/ tests/
```

## License

MIT
