# xiaoA-RAG

[![CI](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml/badge.svg)](https://github.com/RicePiggy7/xiaoA-RAG/actions/workflows/ci.yml)

English | [简体中文](README.md)

A pluggable, observable RAG (Retrieval-Augmented Generation) service framework that exposes its tools over MCP (Model Context Protocol), so AI assistants such as GitHub Copilot and Claude can call them directly.

![xiaoA-RAG overview](docs/images/xiaoA-rag-overview.png)

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Use Cases](#use-cases)
- [Agent Skills](#agent-skills)
- [FAQ](#faq)
- [Status and Contributing](#status-and-contributing)

## Overview

### What this project is

xiaoA-RAG chains the core stages of a RAG system — **retrieval (hybrid search + rerank)**, **multimodal image processing (image captioning)**, **RAG evaluation (Ragas + custom metrics)**, and **generation (LLM response)** — together with the **MCP protocol** into one complete, runnable project.

Because every component sits behind a pluggable interface, you can adapt the system to your own documents and services with configuration changes instead of code changes. See [Use Cases](#use-cases) for common ways to do this.

### Not just code, an engineering approach

The development workflow behind this project is as reusable as the code itself:

- How to write a **DEV_SPEC** (development specification) that drives implementation
- How to use **Skills** to generate code from the spec automatically
- How to use **Skills** for automated testing, packaging, and environment setup
- How to extend a pluggable architecture (for example, toward Agents)

### Core capabilities

| Module | Capability | Notes |
|------|------|------|
| **Ingestion Pipeline** | PDF → Markdown → chunk → transform → embed → upsert | Full ingestion chain with multimodal image captioning |
| **Hybrid Search** | Dense (vectors) + Sparse (BM25) + RRF fusion + rerank | Coarse recall plus fine reranking, two-stage retrieval |
| **MCP Server** | Standard MCP tools | `query_knowledge_hub`, `list_collections`, `get_document_summary` |
| **Dashboard** | Six-page Streamlit app | Overview, data browser, ingestion management, ingestion trace, query trace, evaluation panel |
| **Evaluation** | Ragas + custom metrics | Golden test set regression testing, no tuning by gut feeling |
| **Observability** | Full-link tracing | Every intermediate stage of both ingestion and query paths is visible |
| **Skill-driven workflow** | Coding, testing, packaging, setup in one flow | auto-coder / qa-tester / package / setup / skill-creator cover the full development lifecycle |

### Highlights

**Pluggable end to end.** LLM, embedding, reranker, splitter, vector store, and evaluator each define an abstract interface. Swap backends through the config file with no code changes.

**Hybrid retrieval with rerank.** BM25 handles exact matching of proper nouns; dense embeddings handle synonyms and paraphrase. RRF fuses the two lists, and an optional Cross-Encoder or LLM reranker refines the top results.

**Multimodal via image captioning.** A Vision LLM writes descriptions for images inside documents and stitches them into the chunks, so the plain-text pipeline can answer "search text, get image" queries without a multimodal vector store.

**MCP integration.** The server follows the Model Context Protocol over stdio, so any MCP client — GitHub Copilot, Claude Desktop, Cursor — can call it without custom frontend work.

**Dashboard and evaluation.** A Streamlit dashboard covers data management and trace inspection, and Ragas-based evaluation builds a data-driven feedback loop for retrieval tuning.

**Three-layer test suite.** Unit, integration, and E2E tests cover module logic, module interaction, and full chains (MCP client, dashboard).

For architecture details, module descriptions, and the task schedule, see [DEV_SPEC.md](DEV_SPEC.md).

## Quick Start

### 1. Clone and install

Requires Python 3.10+:

```bash
git clone https://github.com/RicePiggy7/xiaoA-RAG.git
cd xiaoA-RAG

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .            # with test tools: pip install -e ".[dev]"
```

### 2. Configure a provider

Edit `config/settings.yaml` and adjust the `llm` and `embedding` sections.

**Option A — Ollama (local and free, good for a first run)**: install [Ollama](https://ollama.com), pull the models (`ollama pull llama3.1` and `ollama pull nomic-embed-text`), then set:

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

**Option B — OpenAI**: replace `llm.api_key` and `embedding.api_key` with your key (or set the `OPENAI_API_KEY` environment variable). DeepSeek and Azure work the same way; see the comments in `config/settings.yaml`.

### 3. Ingest documents and query

```bash
# Ingest the test documents (or point --path at your own PDF directory)
python scripts/ingest.py --path tests/fixtures/sample_documents

# Query from the command line
python scripts/query.py --query "什么是混合检索"

# Start the dashboard (http://localhost:8501)
python scripts/start_dashboard.py
```

### 4. Connect an MCP client

The MCP server runs over stdio (paths inside the config resolve relative to the repository, so the working directory does not matter):

```bash
python main.py        # or run `mcp-server` after pip install
```

**VS Code (GitHub Copilot)** — add to `.vscode/mcp.json`:

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

**Claude Desktop** — add to `claude_desktop_config.json`:

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

Your client can then call the three tools: `query_knowledge_hub`, `list_collections`, `get_document_summary`.

### 5. Run the tests

```bash
pip install -e ".[dev]"
pytest tests/unit          # unit tests (offline, no API key needed)
pytest tests/integration   # integration tests (some need local services)
```

> **VS Code users**: the built-in **Setup Skill** (`.github/skills/setup/`) can walk you through provider selection, API keys, dependency installation, and config generation — type `setup` in the Copilot chat panel.

## Use Cases

Different backgrounds call for different uses of the project, so pick what fits instead of following one fixed path.

### 1. Learning RAG with a complete reference implementation

The project is a full RAG system, so it works as a practical companion to any RAG book or course: retrieval, generation, vector stores, chunking strategies, and reranking are all implemented and runnable, and the pipeline matches how these topics are usually taught.

### 2. Extending the project as a starting point

The DEV_SPEC lists extension directions. Common ones:

- **Add agent capabilities**: implement the agent side — context handling, tool calling, ReAct logic — and use this project as one module, turning it into an **Agent + RAG** project
- **Show backend engineering skills**: add deployment with a Dockerfile, CI/CD pipelines, monitoring, and log collection
- **Go deeper on retrieval**: extend toward Agentic RAG or Graph RAG, or run more retrieval strategy experiments

A practical suggestion: ingest documents from your own field — finance, law, medicine, or your own work documents — and check retrieval quality. When results are poor, adjust and improve. That process is where most of the learning happens.

### 3. Embedding retrieval into an existing system

Because the server speaks MCP and every component is pluggable, the retrieval capability can run as an independent service: an agent project can treat `query_knowledge_hub` as one of its tools, and an existing backend can use the MCP server as a knowledge-retrieval microservice.

### 4. Trying a spec-driven development workflow

To experience the full **write spec → AI codes → iterate → test** loop, walk through it once with this repo: read the DEV_SPEC structure, change a section, and let an agent re-implement a module from the updated spec. The same spec-driven, skill-automated approach works for any project.

## Agent Skills

The repository ships agent skills that cover the development lifecycle, in `.github/skills/`:

| Skill | Purpose |
|-------|------|
| **auto-coder** | Reads task definitions and architecture rules from the DEV_SPEC, implements code, runs tests, and retries fixes automatically |
| **qa-tester** | Runs the full QA plan (CLI, dashboard UI, MCP protocol, provider switching) |
| **setup** | Interactive setup wizard: provider selection → API key → dependencies → config generation → dashboard launch |
| **package** | One-command cleanup and packaging: removes caches, build artifacts, and sensitive files |
| **skill-creator** | Scaffolding tool for creating new agent skills |

Open the project in an environment that supports skills (VS Code with GitHub Copilot) and they are ready to use. Skills follow one pattern — Markdown knowledge files plus a structured workflow — so you can extend agent capabilities by writing new skills with `skill-creator`.

## FAQ

### 1. How do I switch providers (Qwen, DeepSeek, Ollama)?

The provider layer uses the **factory pattern**, so adding or switching a provider is cheap. Most provider APIs are similar HTTP calls, and most of them follow the OpenAI request format.

Two ways to do it:

1. **Use the Setup Skill (recommended)**: it asks which provider you want, collects the API key, and writes the adapter code and config for you.
2. **Ask an AI to do it**: describe the switch ("switch to Qwen", "configure DeepSeek") and the agent applies the change following the factory structure.

**How it works**: the modules under `src/libs/` (LLM, embedding, reranker) all use factories. A new provider needs three steps: a provider class, a factory registration, and a `settings.yaml` update.

### 2. Custom evaluator and Cross-Encoder reranker

Both modules have their framework in place but have not been fully tested. If you are interested, complete them:

| Module | Status | What it needs |
|------|------|-----------|
| **Custom evaluator** | Framework ready, untested | Define the evaluation method and prepare a test dataset |
| **Cross-Encoder reranker** | Framework ready, untested | Download a local rerank model such as `cross-encoder/ms-marco-MiniLM-L-6-v2` |

### 3. What about bugs and errors?

This is a learning and experimentation project, not tested for production use, so errors can happen.

- **Fixing**: paste the error message into an AI assistant — it solves most of them.
- Bug reports via Issues are welcome.

### 4. Document formats other than PDF (Word, Markdown, HTML)?

The loader layer is pluggable (`BaseLoader`) and ships a PDF loader. The extension points for other formats are already in place: add one loader class per format, following the PDF loader.

For example, tell an AI: "add a Word document loader, following the existing PDF loader" — it can do that.

### 5. How do I integrate it into AI tools (Copilot, Cursor, Claude Code)?

This project is an **MCP server**, so it works with any MCP-capable client (GitHub Copilot, Cursor, Claude Desktop, Claude Code).

The integration is a client-specific MCP config file:

- **Copilot (VS Code)**: have an AI generate the MCP config file
- **Cursor**: import the project; Cursor detects it automatically
- **Claude Code and others**: ask an AI for the config format — details differ, the principle is the same

Understanding the protocol itself also helps: how server and client communicate, and how tools are registered and called.

### 6. General advice: work with AI

Most of the questions above — provider switching, module extension, bug fixing, architecture questions — can be handled with AI assistance:

- **Code**: switching providers, implementing evaluators, fixing bugs
- **Knowledge**: architecture and design pattern questions
- **Extension**: describe a new feature or scenario and have the AI implement it

Working with AI is one of the core ideas this project wants to pass on.

## Status and Contributing

- Core features are complete and covered by a three-layer test suite (unit / integration / E2E), but the project is for learning and experimentation and does not promise production-level stability
- Bug reports, suggestions, and new features via Issues and PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md)
- Fork the project and customize it for your own use case

## License

Released under the [MIT License](LICENSE).
