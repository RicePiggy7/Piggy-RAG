# xiaoA-RAG

[![CI](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml/badge.svg)](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml)

English | [简体中文](README.md)

xiaoA-RAG provides PDF knowledge retrieval over MCP. After you import documents, AI assistants such as GitHub Copilot and Claude can retrieve relevant passages and use source citations in their answers.

The project includes document ingestion, hybrid retrieval, optional reranking, image captioning, a dashboard with tracing, and evaluation. Connect your own documents, replace models, adjust retrieval settings, or extend individual components.

![xiaoA-RAG overview](docs/images/xiaoA-rag-overview.png)

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Use Cases](#use-cases)
- [Agent Skills](#agent-skills)
- [FAQ](#faq)
- [Contributing](#contributing)

## Overview

### From documents to answers

Retrieval-augmented generation (RAG) retrieves relevant document content before a model uses it to answer a question. xiaoA-RAG handles document processing and retrieval, then supplies results through MCP, the protocol AI assistants use to connect to external tools. You can access the knowledge base from your existing assistant.

```text
Ingestion: PDF → parse and extract images → chunk → enrich → vector and BM25 indexes
Query:     AI assistant → MCP query → vector and keyword retrieval → RRF → optional rerank
Response:  passages, citations, and related images → AI assistant composes an answer
```

The query tool returns evidence for the assistant to use. The CLI displays retrieval results directly so you can inspect the returned passages.

### Retrieval and reranking

Vector retrieval finds content by meaning; BM25 matches keywords. Reciprocal Rank Fusion (RRF) combines the two result lists. An optional Cross-Encoder or LLM reranker then reorders candidate passages.

Reranking is disabled by default. Chunk size, retrieval limits, fusion parameters, and the reranker model are configurable.

### Document images

The ingestion pipeline extracts images from PDFs. When a vision model is enabled, image descriptions are added to text chunks for embedding and retrieval. MCP responses can include related images when the retrieved chunks reference them, for clients that support image content.

### Dashboard and tracing

The Streamlit dashboard has six pages: overview, data browser, ingestion management, ingestion traces, query traces, and evaluation.

Import and manage documents, inspect chunks and enrichment, and review indexing, retrieval, fusion, and reranking results. Traces help you compare intermediate results after changing settings.

### Evaluation and components

Custom Evaluator provides retrieval metrics such as Hit Rate and MRR. Ragas evaluates answer faithfulness, relevance, and other metrics. Use your own questions, relevance labels, and answers to compare configurations.

LLM, embedding, reranker, splitter, vector store, and evaluator components have separate interfaces and factories. Select an existing backend through configuration, or implement its interface and register a new backend.

| Component | Implementations |
|-----------|-----------------|
| Text models | OpenAI, Azure OpenAI, Ollama, DeepSeek |
| Embeddings | OpenAI, Azure OpenAI, Ollama |
| Vision models | OpenAI, Azure OpenAI |
| Document parsing | PDF |
| Text splitting | Recursive splitting |
| Vector storage | Chroma |
| Reranking | Cross-Encoder, LLM |
| Evaluation | Custom, Ragas, composite evaluation |

See [DEV_SPEC.md](DEV_SPEC.md) for architecture and module details, and [CONTRIBUTING.md](CONTRIBUTING.md#项目结构速览) for the source directory layout.

## Quick Start

### 1. Clone and install

Requires Python 3.10+. CI covers Python 3.10, 3.11, and 3.12.

```bash
git clone https://github.com/RicePiggy7/xiaoA-RAG.git
cd xiaoA-RAG

python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows, activate the environment with `.venv\Scripts\activate`. Run the following commands from the project root.

### 2. Configure models

Edit `config/settings.yaml`. Choose local models or OpenAI below.

**Local models: Ollama**

[Install and start Ollama](https://ollama.com), then download a text model and an embedding model:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

Replace the entire `llm`, `embedding`, and `vision_llm` sections with the following. Keep the other sections unchanged.

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

This configuration uses local models for text processing and embeddings, with image captioning disabled. The default Ollama address is `http://localhost:11434`; set `OLLAMA_BASE_URL` to use a different address.

**Cloud models: OpenAI**

Replace the same three sections with:

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

Set the `OPENAI_API_KEY` environment variable, or fill in `api_key` in all three sections. A nonempty configuration key takes precedence over the environment variable. Cloud model calls incur the provider's API charges.

For the official OpenAI service, remove `azure_endpoint`, `deployment_name`, and `api_version` from the original configuration. Keeping `azure_endpoint` makes the OpenAI adapter use Azure-compatible mode.

DeepSeek can serve as the text model; choose OpenAI, Azure OpenAI, or Ollama separately for embeddings. See the [setup configuration guide](.github/skills/setup/references/provider_profiles.md) for Azure fields and other model options.

### 3. Import documents and query

```bash
# Import the sample PDFs
python scripts/ingest.py --path tests/fixtures/sample_documents

# Inspect retrieved passages and intermediate results
python scripts/query.py --query "What is hybrid search?" --verbose

# Start the dashboard
python scripts/start_dashboard.py
```

The dashboard defaults to [http://localhost:8501](http://localhost:8501). Ingestion reports processed files and chunk counts. Query results include passages, scores, and source paths.

To import your own documents, point `--path` to a PDF or directory. Use `--collection` to separate knowledge bases, with the same name for ingestion and retrieval:

```bash
python scripts/ingest.py --path /path/to/pdfs --collection my_docs
python scripts/query.py --query "A question about these documents" --collection my_docs
```

### 4. Connect an AI assistant

The MCP server uses stdio and is launched by the client. You can also start it with `python main.py` or the installed `mcp-server` command.

**VS Code (GitHub Copilot)**

Add to the project's `.vscode/mcp.json`:

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

Add to `claude_desktop_config.json`, replacing the paths with absolute paths on your machine:

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

On Windows, Python is at `.venv\Scripts\python.exe`; escape backslashes as `\\` in JSON. If you use an environment variable for the API key, make sure the client-launched process receives it. You can pass it through the client's MCP environment settings.

Three tools are available:

| Tool | Purpose |
|------|---------|
| `query_knowledge_hub` | Retrieve passages, citations, and related images |
| `list_collections` | List document collections and statistics |
| `get_document_summary` | Get summary information for a document |

Try asking your assistant: “Search the xiaoA-RAG knowledge base, explain hybrid search, and cite the sources.”

### 5. Run tests

```bash
pip install -e ".[dev]"

pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

Unit tests mock external calls. Integration and E2E tests use model services, API credentials, or indexed data as required by each case. Tests marked `llm` call real models. CI runs unit tests and basic code checks.

## Use Cases

### Give AI assistants access to documents

Import product manuals, technical references, or business PDFs and connect through MCP. The assistant can retrieve relevant content and cite document sources in its answers.

### Adjust retrieval quality

Use your own documents and questions to inspect vector, BM25, fusion, and reranking results. Adjust chunk size, retrieval limits, and model selection, then compare metrics with labeled data.

### Integrate with an agent or another project

An agent can use `query_knowledge_hub` as its retrieval tool while managing context, conversations, and task execution itself. You can also reuse ingestion or retrieval modules and replace components through their interfaces.

## Agent Skills

The repository includes [DEV_SPEC.md](DEV_SPEC.md) and [Agent Skills](.github/skills/). The specification describes architecture, module interfaces, and development tasks. Skills provide workflows for AI coding tools that support them.

| Skill | Purpose |
|-------|---------|
| [auto-coder](.github/skills/auto-coder/SKILL.md) | Implement modules from the specification, run tests, and resolve errors |
| [qa-tester](.github/skills/qa-tester/SKILL.md) | Check CLI, dashboard, MCP, and model switching against the test plan |
| [setup](.github/skills/setup/SKILL.md) | Guide model selection, credentials, dependency installation, and service startup |
| [package](.github/skills/package/SKILL.md) | Clean caches, build artifacts, and sensitive configuration for distribution |
| [skill-creator](.github/skills/skill-creator/SKILL.md) | Create a new skill directory and instructions |

Open the project in a tool that supports Agent Skills and select a skill for configuration, development, or verification. When extending a module, you can update its interfaces and acceptance criteria in the specification before asking an agent to implement it.

## FAQ

### How do I switch models or add a backend?

Select an existing backend through `provider` and `model`. To add a backend, implement the relevant interface in `src/libs/`, register it with the factory, and add configuration and tests. See the [new provider guide](.github/skills/setup/references/new_provider_guide.md).

After changing embedding models, regenerate document vectors with the new model. Use a new collection to avoid mixing embeddings; vectors from different models are incompatible even when their dimensions match.

### How do I enable Cross-Encoder reranking?

Install the model dependency:

```bash
pip install sentence-transformers
```

Replace the `rerank` section with:

```yaml
rerank:
  enabled: true
  provider: "cross_encoder"
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
  top_k: 5
```

The model downloads on first use. You can also specify a local model path. Choose a model suited to the language of your documents and queries.

### How do I evaluate my knowledge base?

Choose an evaluator in the dashboard or run `scripts/evaluate.py`. See [golden_test_set.json](tests/fixtures/golden_test_set.json) for the test set format.

Hit Rate and MRR need relevant `expected_chunk_ids` for each question. Ragas answer evaluation needs the actual answer being evaluated and model configuration. Contributions of domain questions, relevance labels, and evaluation methods are welcome.

### How do I support Word, Markdown, or HTML?

`BaseLoader` defines the parsing interface, and the current ingestion pipeline uses `PdfLoader`. Add a loader, connect format selection to the pipeline, and update CLI file filtering and dashboard upload types.

### What should I check when something fails or results are poor?

For connection failures, check the service address, model name, and API credentials. For empty results, confirm that documents were imported and that the query uses the same collection and embedding model. For irrelevant results, inspect the returned passages at each stage in query traces.

Report issues with reproduction steps, environment details, and logs with sensitive information removed. For retrieval problems, include shareable sample documents, a query, and expected results when possible.

## Contributing

Contributions based on your own documents and workflows are welcome, along with reports of problems and improvements.

Areas to contribute include:

- Additional document formats and better PDF table and image parsing.
- Model adapters, vector storage backends, and retrieval strategies.
- Evaluation questions and relevance labels for comparing configurations.
- Document management, trace displays, and deployment workflows.
- Bug fixes, tests, and documentation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the Issue and PR workflow.

## License

Released under the [MIT License](LICENSE).
