# 贡献指南

感谢你愿意为 xiaoA-RAG 贡献代码！这个项目欢迎 Issue 反馈、Bug 修复、文档改进和新功能。

## 开发环境搭建

```bash
git clone https://github.com/RicePiggy7/xiaoA-RAG.git
cd xiaoA-RAG

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

配置 Provider（Ollama 本地免费 / OpenAI / DeepSeek 等）见 [README 快速开始](README.md#快速开始)。

## 提交前检查清单

1. **测试通过**：

   ```bash
   pytest tests/unit
   ```

   新功能请附带单元测试（放在 `tests/unit/`，文件名 `test_*.py`）。集成测试（`tests/integration`）部分依赖本地服务，CI 只跑单元测试。

2. **Lint 通过**（CI 使用最小规则集：语法错误 + 未定义名）：

   ```bash
   ruff check --select E9,F63,F7,F82 src tests scripts main.py
   ```

   > 注意：`pyproject.toml` 中的完整 ruff 配置存在约 7k 处历史遗留违规，尚未全量启用。**新增/修改的代码请尽量符合完整规则**，不要新增违规；全量清理欢迎单独提 PR。

3. **文档同步**：改动了配置项、CLI 参数或架构行为的，请同步更新 `README.md` 和 `DEV_SPEC.md` 对应章节。

## 分支与提交约定

- 从 `main` 拉分支开发，PR 回 `main`
- 提交信息建议使用约定式前缀：`fix:` / `feat:` / `docs:` / `test:` / `refactor:` / `chore:`
- 一个 PR 只做一件事，方便 review

## 项目结构速览

```
src/
  core/          # 查询引擎（混合检索/重排/融合）、响应构建、配置、追踪
  ingestion/     # 摄取流水线（加载/切分/变换/嵌入/存储）
  libs/          # 可插拔组件抽象层（LLM/Embedding/向量库/Reranker/...）
  mcp_server/    # MCP 协议服务与三个内置工具
  observability/ # Dashboard 与评估体系
tests/           # unit / integration / e2e 三层测试
.github/skills/  # Agent Skills（auto-coder / qa-tester / setup / package / skill-creator）
```

新增 Provider 或组件的扩展方式（工厂模式 + `settings.yaml` 注册）参见 `DEV_SPEC.md` 的架构章节。

## 报告 Issue

- Bug 请用 Bug Report 模板，附上复现步骤、Python 版本和完整报错
- 功能建议先开 Discussion 或 Feature Request 描述使用场景，避免直接写代码

## 行为准则

保持友善和就事论事。技术讨论对事不对人。
