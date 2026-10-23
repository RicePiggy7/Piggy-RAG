# xiaoA-RAG

[![CI](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml/badge.svg)](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml)

[简体中文](README.md) | [English](README_EN.md)

xiaoA-RAG 是一个通过 MCP 提供 PDF 知识检索能力的 RAG 项目。导入文档后，GitHub Copilot、Claude 等 AI 助手可以检索相关内容，结合来源引用组织回答。

项目包含文档摄取、混合检索、可选重排、图片描述、可视化追踪和评估。大家可以直接接入自己的文档，也可以根据业务需要替换模型、调整检索策略或扩展组件。仓库同时提供 DEV_SPEC 和 Agent Skills，可以用 AI 工具完成配置、开发和验证的完整流程。

![xiaoA-RAG overview](docs/images/xiaoA-rag-overview.png)

## 目录

- [项目概述](#项目概述)
- [快速开始](#快速开始)
- [使用场景](#使用场景)
- [Agent Skills](#agent-skills)
- [常见问题](#常见问题)
- [参与贡献](#参与贡献)

## 项目概述

### 文档如何成为回答的依据

RAG 是检索增强生成：先从文档中检索相关内容，再由模型结合这些内容回答问题。xiaoA-RAG 负责文档处理和知识检索，通过 MCP 将检索结果提供给 AI 助手。MCP 是 AI 助手连接外部工具的协议，接入后可以继续在已有的对话环境中使用知识库。

整个流程分为文档摄取和查询两条链路：

```text
文档摄取：PDF → 解析与图片提取 → 文本分块 → 内容增强 → 向量索引与 BM25 索引
查询流程：AI 助手 → MCP 查询 → 向量检索与关键词检索 → RRF 融合 → 可选重排
返回内容：文档片段、来源引用和相关图片 → AI 助手组织回答
```

命令行查询可以直接查看检索结果，方便检查召回内容。

### 检索与重排

向量检索根据语义寻找相关内容，BM25 根据关键词进行匹配。项目通过 RRF 合并两路结果，也可以继续使用 Cross-Encoder 或 LLM 对候选片段重新排序。

重排默认关闭，可以根据文档内容和查询需求启用。分块长度、召回数量、融合参数和重排模型均可通过配置调整。

### 文档图片处理

摄取 PDF 时，项目会提取图片。启用视觉模型后，图片描述会加入文本块，参与后续的向量化和检索。查询命中关联片段时，MCP 工具可以同时返回图片，供支持图片内容的客户端使用。

### 可视化管理与追踪

基于 Streamlit 的 Dashboard 提供六个页面：系统总览、数据浏览、摄取管理、摄取追踪、查询追踪和评估面板。

大家可以在其中导入和管理文档，查看分块、内容增强、索引写入，以及查询时的召回、融合和重排结果。调整配置后，可以通过追踪记录比较中间结果的变化。

### 评估与组件扩展

Custom Evaluator 提供 Hit Rate 和 MRR 等检索指标，Ragas 用于评估回答的忠实度、相关性等。评估时可以使用自己的问题、相关片段标注和待评估回答，对比不同配置下的结果。

LLM、Embedding、Reranker、Splitter、VectorStore 和 Evaluator 均有独立接口与工厂。已有后端通过配置选择，新增后端可以实现对应接口并注册到工厂。

| 组件 | 已有实现 |
|------|----------|
| 文本模型 | OpenAI、Azure OpenAI、Ollama、DeepSeek |
| Embedding | OpenAI、Azure OpenAI、Ollama |
| 视觉模型 | OpenAI、Azure OpenAI |
| 文档解析 | PDF |
| 文本切分 | 递归切分 |
| 向量存储 | Chroma |
| 重排 | Cross-Encoder、LLM |
| 评估 | Custom、Ragas，以及组合评估 |

架构设计和模块说明见 [DEV_SPEC.md](DEV_SPEC.md)，源码目录说明见 [CONTRIBUTING.md](CONTRIBUTING.md#项目结构速览)。

## 快速开始

### 1. 克隆并安装

需要 Python 3.10+，CI 覆盖 Python 3.10、3.11 和 3.12。

```bash
git clone https://github.com/RicePiggy7/xiaoA-RAG.git
cd xiaoA-RAG

python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows 使用 `.venv\Scripts\activate` 激活虚拟环境。后续命令均在项目根目录执行。

### 2. 配置模型

配置文件为 `config/settings.yaml`。下面提供本地模型和 OpenAI 两种方式。

**本地模型：Ollama**

先[安装并启动 Ollama](https://ollama.com)，下载文本模型和 Embedding 模型：

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

将配置文件中的 `llm`、`embedding` 和 `vision_llm` 三个配置段完整替换为以下内容，其余配置保持原样：

```yaml
llm:
  provider: "ollama"
  model: "llama3.1"
  temperature: 0.0
  max_tokens: 4096
  base_url: "http://localhost:11434"

embedding:
  provider: "ollama"
  model: "nomic-embed-text"
  dimensions: 768
  base_url: "http://localhost:11434"

vision_llm:
  enabled: false
  provider: "openai"
  model: "gpt-4o"
  max_image_size: 2048
```

这份配置使用本地模型处理文本和生成向量，并关闭图片描述。Ollama 默认地址为 `http://localhost:11434`；使用其他地址时，设置环境变量 `OLLAMA_BASE_URL`。

**云端模型：OpenAI**

将同样的三个配置段完整替换为以下内容：

```yaml
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.0
  max_tokens: 4096
  api_key: null

embedding:
  provider: "openai"
  model: "text-embedding-ada-002"
  dimensions: 1536
  api_key: null

vision_llm:
  enabled: true
  provider: "openai"
  model: "gpt-4o"
  max_image_size: 2048
  api_key: null
```

设置 `OPENAI_API_KEY` 环境变量，或者在这三个配置段中填写自己的 `api_key`。配置中的非空 Key 优先于环境变量。调用云端模型会产生相应的 API 费用。

使用 OpenAI 官方服务时，请移除原配置中的 `azure_endpoint`、`deployment_name` 和 `api_version`；保留 `azure_endpoint` 会使 OpenAI 适配器进入 Azure 兼容模式。

DeepSeek 可用于文本模型，Embedding 需要单独选择 OpenAI、Azure OpenAI 或 Ollama。Azure 配置字段和其他模型适配说明见 [Setup 配置指南](.github/skills/setup/references/provider_profiles.md)。

### 3. 导入文档并查询

```bash
# 导入仓库中的示例 PDF
python scripts/ingest.py --path tests/fixtures/sample_documents

# 查看检索结果及各阶段的中间结果
python scripts/query.py --query "什么是混合检索" --verbose

# 启动可视化管理平台
python scripts/start_dashboard.py
```

Dashboard 默认地址为 [http://localhost:8501](http://localhost:8501)。摄取脚本会输出处理文件数和生成的文本块数量；查询结果包含片段、分数和来源路径。

使用自己的文档时，将 `--path` 改为 PDF 文件或目录。可以通过 `--collection` 区分不同知识库，导入和查询时使用相同名称：

```bash
python scripts/ingest.py --path /path/to/pdfs --collection my_docs
python scripts/query.py --query "这里填写与文档相关的问题" --collection my_docs
```

### 4. 接入 AI 助手

MCP Server 使用 stdio 通信，由客户端启动。安装后也可以通过 `python main.py` 或 `mcp-server` 启动服务。

**VS Code（GitHub Copilot）**

在项目的 `.vscode/mcp.json` 中添加：

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

**Claude Desktop**

在 `claude_desktop_config.json` 中添加，并替换为本机的绝对路径：

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

Windows 中的 Python 路径为 `.venv\Scripts\python.exe`，JSON 内的反斜杠需要写成 `\\`。使用环境变量提供 API Key 时，需要确保客户端启动的进程能够读取该变量，也可以通过客户端的 MCP 环境变量配置传入。

接入后提供三个工具：

| 工具 | 用途 |
|------|------|
| `query_knowledge_hub` | 根据问题检索文档，返回片段、引用和关联图片 |
| `list_collections` | 查看已有文档集合及统计信息 |
| `get_document_summary` | 获取指定文档的摘要信息 |

可以在助手中提出：“请查询 xiaoA-RAG 知识库，解释什么是混合检索，并注明来源。”

### 5. 运行测试

```bash
pip install -e ".[dev]"

pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

单元测试通过 Mock 隔离外部调用。集成测试和端到端测试按用例需要使用模型服务、API 凭据或已导入的数据；带有 `llm` 标记的测试会调用真实模型。CI 运行单元测试和基础代码检查。

## 使用场景

### 为 AI 助手提供文档知识

将产品手册、技术资料或业务 PDF 导入知识库，通过 MCP 接入已有助手。助手在回答问题时可以检索相关内容，并引用文档来源。

### 调整检索效果

使用自己的文档和问题，查看向量检索、BM25、融合和重排的结果。根据追踪记录调整分块长度、召回数量和模型选择，再通过标注数据比较检索指标。

### 集成到 Agent 或其他项目

已有 Agent 可以将 `query_knowledge_hub` 注册为知识检索工具，自行处理上下文组织、多轮对话和任务执行。也可以复用摄取或检索模块，按照现有接口替换组件。

## Agent Skills

仓库同时提供 [DEV_SPEC.md](DEV_SPEC.md) 和位于 [`.github/skills/`](.github/skills/) 的 Agent Skills。DEV_SPEC 记录架构、模块接口和开发任务，Skills 为支持该机制的 AI 编程工具提供操作流程。

| Skill | 用途 |
|-------|------|
| [auto-coder](.github/skills/auto-coder/SKILL.md) | 根据开发规格实现模块、运行测试并处理错误 |
| [qa-tester](.github/skills/qa-tester/SKILL.md) | 按测试计划检查 CLI、Dashboard、MCP 和模型切换 |
| [setup](.github/skills/setup/SKILL.md) | 引导模型选择、凭据配置、依赖安装和服务启动 |
| [package](.github/skills/package/SKILL.md) | 清理缓存、构建产物和敏感配置，整理分发文件 |
| [skill-creator](.github/skills/skill-creator/SKILL.md) | 创建新的 Skill 目录与说明文件 |

使用支持 Agent Skills 的工具打开项目后，可以指定相应 Skill 协助配置、开发和验证。扩展模块时，也可以先更新开发规格中的接口和验收要求，再交由 Agent 实现。

## 常见问题

### 如何切换模型或增加后端？

已有模型后端通过配置中的 `provider` 和 `model` 选择。新增后端时，在 `src/libs/` 中实现对应接口、注册到工厂，并补充配置和测试。具体流程见 [新增 Provider 指南](.github/skills/setup/references/new_provider_guide.md)。

切换 Embedding 模型后，需要使用新模型重新生成文档向量。建议使用新的集合，避免混用不同模型产生的向量；即使维度相同，不同模型的向量也不能直接混用。

### 如何启用 Cross-Encoder 重排？

先安装模型依赖：

```bash
pip install sentence-transformers
```

然后替换配置中的 `rerank` 段：

```yaml
rerank:
  enabled: true
  provider: "cross_encoder"
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
  top_k: 5
```

首次使用会下载模型，也可以指定本地模型路径。选择模型时需要考虑文档和查询的语言。

### 如何评估自己的知识库？

在 Dashboard 的评估面板中选择评估方式，或使用 `scripts/evaluate.py` 执行评估。测试集格式见 [golden_test_set.json](tests/fixtures/golden_test_set.json)。

计算 Hit Rate 和 MRR 时，需要为问题填写相关片段的 `expected_chunk_ids`。使用 Ragas 评估回答时，需要提供实际待评估的回答和相应的模型配置。大家可以补充自己领域的问题、标注和评估方法。

### 如何支持 Word、Markdown 或 HTML？

文档解析接口为 `BaseLoader`，当前摄取流程使用 `PdfLoader`。支持新格式时，需要实现对应的 Loader，并在摄取流程中接入格式选择，同时更新 CLI 的文件筛选和 Dashboard 的上传类型。

### 遇到错误或检索结果不理想怎么办？

连接失败时，检查模型服务地址、模型名称和 API 凭据。查询没有结果时，确认文档已经导入，并且查询使用了相同的集合和 Embedding 模型。结果不相关时，可以通过查询追踪查看各阶段返回的片段。

欢迎通过 Issue 提供复现步骤、运行环境和脱敏后的错误日志。涉及检索效果的问题，可以附上便于公开的文档样例、查询和预期结果，方便定位和改进。

## 参与贡献

欢迎大家结合自己的文档和业务场景继续优化项目，也欢迎分享使用过程中的问题和改进结果。

可以参与的方向包括：

- 扩展文档格式，改进 PDF 中表格和图片的解析。
- 增加模型适配、向量存储后端和检索策略。
- 补充评测问题与相关片段标注，对比不同配置的检索效果。
- 优化数据管理、追踪展示和部署流程。
- 修复问题，完善测试和使用文档。

提交 Issue 和 PR 的流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

本项目基于 [MIT License](LICENSE) 开源。
