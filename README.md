# xiaoA-RAG

> 一个可插拔、可观测的模块化 RAG（检索增强生成）服务框架，通过 MCP（Model Context Protocol）协议对外暴露工具接口，支持 Copilot / Claude 等 AI 助手直接调用。

---

## 📖 目录

- [项目概述](#-项目概述)
- [快速开始](#-快速开始)
- [使用场景](#-使用场景)
- [Agent Skills](#-agent-skills)
- [常见问题](#-常见问题)
- [项目状态与贡献](#-项目状态与贡献)

---

## 🏗️ 项目概述

### 这个项目是什么

xiaoA-RAG 将 RAG 系统的核心环节——**检索（Hybrid Search + Rerank）**、**多模态视觉处理（Image Captioning）**、**RAG 评估（Ragas + Custom）**、**生成（LLM Response）**——以及应用协议 **MCP（Model Context Protocol）** 串联为一个完整的、可运行的工程项目。

**项目的一大亮点是极易适配到你自己的业务中**。得益于全链路可插拔架构，你可以快速将它结合到自己已有的项目里，具体的使用方式见 [使用场景](#-使用场景)。

### 不只是代码，更是一套工程化思路

**比这个项目本身更有参考价值的，是它背后的工程化思路**：

- 如何编写 **DEV_SPEC**（开发规格文档）来驱动开发
- 如何用 **Skill** 基于 Spec 自动完成代码编写
- 如何用 **Skill** 进行自动化测试、打包、环境配置
- 如何基于可插拔架构进行扩展（比如扩展到 Agent）

### 核心能力一览

| 模块 | 能力 | 说明 |
|------|------|------|
| **Ingestion Pipeline** | PDF → Markdown → Chunk → Transform → Embedding → Upsert | 全链路数据摄取，支持多模态图片描述（Image Captioning） |
| **Hybrid Search** | Dense (向量) + Sparse (BM25) + RRF Fusion + Rerank | 粗排召回 + 精排重排的两段式检索架构 |
| **MCP Server** | 标准 MCP 协议暴露 Tools | `query_knowledge_hub`、`list_collections`、`get_document_summary` |
| **Dashboard** | Streamlit 六页面管理平台 | 系统总览 / 数据浏览 / Ingestion 管理 / 摄取追踪 / 查询追踪 / 评估面板 |
| **Evaluation** | Ragas + Custom 评估体系 | 支持 golden test set 回归测试，拒绝"凭感觉"调优 |
| **Observability** | 全链路白盒化追踪 | Ingestion 与 Query 两条链路的每一个中间状态透明可见 |
| **Skill 驱动全流程** | 从编写到测试、打包、配置一键完成 | auto-coder / qa-tester / package / setup / skill-creator 等 Skill 覆盖完整开发生命周期 |

### 技术亮点

**🔌 全链路可插拔架构**：LLM / Embedding / Reranker / Splitter / VectorStore / Evaluator 每一个核心环节均定义了抽象接口，支持"乐高积木式"替换，通过配置文件一键切换后端，零代码修改。

**🔍 混合检索 + 重排**：BM25 稀疏检索解决专有名词精确匹配 + Dense Embedding 解决同义词语义匹配，RRF 融合后可选 Cross-Encoder / LLM Rerank 精排，平衡查全率与查准率。

**🖼️ 多模态图像处理**：采用 Image-to-Text 策略，利用 Vision LLM 自动生成图片描述并缝合进 Chunk，复用纯文本 RAG 链路即可实现"搜文字出图"。

**📡 MCP 生态集成**：遵循 Model Context Protocol 标准，可直接对接 GitHub Copilot、Claude Desktop 等 MCP Client，零前端开发，一次开发处处可用。

**📊 可视化管理 + 自动化评估**：Streamlit Dashboard 提供完整的数据管理与链路追踪能力，集成 Ragas 等评估框架，建立基于数据的迭代反馈回路。

**🧪 三层测试体系**：Unit / Integration / E2E 分层测试，覆盖独立模块逻辑、模块间交互、完整链路（MCP Client / Dashboard）。

> 📖 详细架构设计、模块说明和任务排期请参阅 [DEV_SPEC.md](DEV_SPEC.md)

---

## 🚀 快速开始

### 1. 克隆并安装

要求 Python 3.10+：

```bash
git clone https://github.com/RicePiggy7/xiaoA-RAG.git
cd xiaoA-RAG

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .            # 加测试工具: pip install -e ".[dev]"
```

### 2. 配置 Provider

编辑 `config/settings.yaml`，按你想用的 Provider 修改 `llm` 和 `embedding` 两段。

**方式 A — Ollama（本地免费，推荐先跑通）**：先[安装 Ollama](https://ollama.com) 并拉取模型（`ollama pull llama3.1` 和 `ollama pull nomic-embed-text`），然后：

```yaml
llm:
  provider: "ollama"
  model: "llama3.1"
  base_url: "http://localhost:11434"

embedding:
  provider: "ollama"
  model: "nomic-embed-text"
  dimensions: 768
  base_url: "http://localhost:11434"
```

**方式 B — OpenAI**：把 `llm.api_key` 和 `embedding.api_key` 换成你的 Key（或设置环境变量 `OPENAI_API_KEY`）。DeepSeek/Azure 同理，见 `config/settings.yaml` 内注释。

### 3. 摄取文档并查询

```bash
# 摄取测试文档（也可以指向你自己的 PDF 目录）
python scripts/ingest.py --path tests/fixtures/sample_documents

# 命令行查询
python scripts/query.py --query "什么是混合检索"

# 启动可视化管理平台（http://localhost:8501）
python scripts/start_dashboard.py
```

### 4. 接入 MCP 客户端

MCP Server 通过 stdio 传输启动（配置路径按代码仓库内文件解析，与工作目录无关）：

```bash
python main.py        # 或 pip install 后直接运行 mcp-server
```

**VS Code（GitHub Copilot）** — 在 `.vscode/mcp.json` 中添加：

```json
{
  "servers": {
    "xiaoA-RAG": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/main.py"]
    }
  }
}
```

**Claude Desktop** — 在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "xiaoA-RAG": {
      "command": "/absolute/path/to/xiaoA-RAG/.venv/bin/python",
      "args": ["/absolute/path/to/xiaoA-RAG/main.py"]
    }
  }
}
```

之后即可在客户端里调用 `query_knowledge_hub` / `list_collections` / `get_document_summary` 三个工具。

### 5. 运行测试

```bash
pip install -e ".[dev]"
pytest tests/unit          # 单元测试（离线，不需要 API Key）
pytest tests/integration   # 集成测试（部分需要本地服务）
```

> 💡 **VS Code 用户**：也可以用项目内置的 **Setup Skill**（`.github/skills/setup/`）一键完成 Provider 选择 → API Key → 依赖安装 → 配置生成的引导流程，在 Copilot 对话框输入 `setup` 即可。

---

## 🎯 使用场景

不同背景的使用者对项目的用法不同，**请灵活使用，切忌生搬硬套**。

### 1. 学习 RAG —— 把项目当作 RAG 全流程的学习材料

这个项目本身就是一个完整的 RAG 系统，可以作为学习 RAG 的实战参考。RAG 的典型环节——检索、生成、向量数据库、分块策略、重排序等——本项目都完整实现了，你可以配合任意一本 RAG 书籍或课程对照学习，因为流程是通的。

### 2. 以本项目为起点进行扩展

你可以把这个项目作为起点，根据自己的方向进行针对性扩展。DEV_SPEC 中也写了扩展方向，这里列几个常见的：

- **补充 Agent 能力**：自己实现 Agent 端，做一些上下文处理、Tool Calling、ReAct 逻辑，把本项目作为 Agent 的一个模块和能力，变成一个 **Agent + RAG** 的项目
- **展示后端工程能力**：加上后端部署能力，写 Dockerfile，做 CI/CD 流水线，加上监控和日志收集
- **把 RAG 做深入**：扩展到 Agentic RAG、Graph RAG 等高级形态，或者在检索策略上做更多优化实验

> **建议**：把你自己领域的文档（金融、法律、医疗，或者你的业务文档）丢进去，看一下检索效果。如果效果不好，再去调整和改进——这个过程本身是最好的学习。

### 3. 融入现有项目 —— 把 RAG 能力集成到你已有的系统中

得益于 MCP 协议和可插拔架构，本项目的检索能力可以作为一个独立服务嵌入你已有的系统：Agent 项目可以把 `query_knowledge_hub` 作为其中一个 Tool；已有后端可以把 MCP Server 作为知识检索微服务。

### 4. 体验 Spec 驱动开发工作流

如果你想体验**文档设计 → AI 写代码 → 改进迭代 → 测试**的完整工作流，可以基于本项目做一次完整重走：阅读 DEV_SPEC 的结构，尝试修改文档、让 Agent 基于修改后的 Spec 重新实现某个模块。这套 **Spec 驱动开发 + Skill 自动化** 的方法论适用于任何项目。

---

## 🤖 Agent Skills

本项目内置了覆盖完整开发生命周期的 Agent Skills，位于 `.github/skills/`：

| Skill | 用途 |
|-------|------|
| **auto-coder** | 读取 DEV_SPEC 中的任务定义与架构规范，自动实现代码并运行测试，支持自动修复 |
| **qa-tester** | 基于 QA_TEST_PLAN 自动执行全类型测试（CLI / Dashboard UI / MCP 协议 / Provider 切换） |
| **setup** | 交互式一键配置向导：Provider 选择 → API Key → 依赖安装 → 配置生成 → Dashboard 启动 |
| **package** | 一键清理打包，移除缓存/构建产物/敏感信息，生成可分发代码包 |
| **skill-creator** | 创建新的 Agent Skill 的脚手架工具 |

在 VS Code（GitHub Copilot）等支持 Skill 的环境中打开项目即可使用。Skill 采用"Markdown 知识文件 + 结构化工作流"的统一范式，你也可以参照 `skill-creator` 编写自己的 Skill 来扩展 Agent 能力。

---

## ❓ 常见问题

### 1. 如何切换 Provider（比如换成 Qwen / DeepSeek / Ollama）？

项目从架构设计上使用了**工厂模式（Factory Pattern）**，Provider 的扩展和切换非常方便。不同 API 本质上都是类似的 HTTP 请求，甚至大多数都遵循 OpenAI 的请求格式。

**具体操作方式有两种：**

1. **使用 Setup Skill（推荐）**：运行一键 Setup Skill，AI 会主动询问你想用哪个 Provider，引导你填入 API Key，然后自动帮你完成代码适配和配置生成。
2. **直接让 AI 帮你改**：把你想切换的 Provider 告诉 AI（如 "帮我切换到 Qwen" 或 "帮我配置 DeepSeek"），AI 能根据工厂模式的架构自动完成代码编写。

> **原理说明**：项目的 `src/libs/` 下的 LLM、Embedding、Reranker 等模块都使用工厂模式，新增一个 Provider 只需要：① 新增一个 Provider 类；② 在工厂注册；③ 更新 `settings.yaml` 配置。

### 2. 项目评估（Custom Evaluator）与 Cross-Encoder Reranker 部分

这两个模块的**框架代码已经搭好，但尚未经过完整测试**，感兴趣的可以自行完善：

| 模块 | 状态 | 需要做什么 |
|------|------|-----------|
| **自定义评估（Custom Evaluator）** | 框架已有，未测试 | 定义评估方法，准备对应的测试数据集 |
| **Cross-Encoder Reranker** | 框架已有，未测试 | 需要下载本地重排模型（如 `cross-encoder/ms-marco-MiniLM-L-6-v2`） |

### 3. 项目报错 / Bug 怎么办？

**这是一个学习/实验性质的项目，未经过生产级的广泛测试。** 遇到报错是正常的。

- **如何修复**：最简单的方式是**把错误信息直接丢给 AI**，绝大多数问题 AI 都能帮你修复。
- 也欢迎提 Issue 反馈问题。

### 4. 想摄取 PDF 以外的文档格式（Word / Markdown / HTML 等）怎么办？

项目的 Loader 层采用了可插拔的抽象设计（`BaseLoader`），目前默认实现了 PDF Loader。如果你需要支持 Word、Markdown、HTML 等其他格式，整体架构已经设计好了扩展点，新增一个对应的 Loader 实现即可。

比如告诉 AI："帮我新增一个 Word 文档的 Loader，参考现有的 PDF Loader 实现"，AI 完全可以搞定。

### 5. 如何集成到 AI 工具中（Copilot / Cursor / Claude Code 等）？

本项目是一个 **MCP Server**，可以集成到任何支持 MCP 协议的 AI 工具和 Agent 中（GitHub Copilot、Cursor、Claude Desktop / Claude Code 等）。

本质上就是给不同的工具写一个 MCP 的配置文件：

- **Copilot（VS Code）**：让 AI 帮你生成 MCP 配置文件即可
- **Cursor**：直接导入项目，Cursor 会自动识别
- **Claude Code / 其他框架**：问 AI 怎么配置，每个工具的配置方式略有不同，但原理都一样

也推荐去理解 MCP 协议的原理——Server 和 Client 之间如何通信、Tool 怎么注册和调用。

### 6. 通用建议：善用 AI

上述大多数问题（Provider 切换、模块扩展、Bug 修复、架构理解）**AI 都能解决**：

- 🔧 **代码层面**：让 AI 帮你切换 Provider、实现评估方法、修复 Bug
- 📖 **知识层面**：项目架构问题、设计模式问题，都可以问 AI 获取解释
- 🚀 **扩展层面**：想加新功能或适配新场景，描述清楚需求让 AI 帮你实现

> 这也是这个项目想要传达的核心理念之一——**学会与 AI 协作开发**。

---

## 📌 项目状态与贡献

- 项目核心功能已完成并通过三层测试（Unit / Integration / E2E），但属于**学习/实验性质**，不承诺生产级稳定性
- 欢迎通过 Issue 和 PR 反馈 Bug、改进建议与新功能，贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)
- 鼓励大家 Fork 后结合自己的业务场景做定制化扩展

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。
