# hello-my-deep_agents

> 面向 **Java 工程师 / Python 入门者** 的 **DeepAgents 全流程实战教程**
> Python + LangChain + DeepAgents + 阿里云通义千问 — 学完就能干活，代码直接 run

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)]()
[![LangChain](https://img.shields.io/badge/LangChain-0.3.x-1C3C3C?logo=langchain&logoColor=white)]()
[![DeepAgents](https://img.shields.io/badge/DeepAgents-LangChain--AI-2EA44F)]()
[![Qwen](https://img.shields.io/badge/LLM-Qwen--Plus-FF6A00)]()

---

## 一句话定位

| 问题 | 本教程的回答 |
|---|---|
| **谁适合学** | 有 Java/Spring 基础 / 想转 LLM 应用开发的工程师 |
| **学完能干嘛** | 用 Python + DeepAgents 独立交付一个**有规划能力、能调工具、有记忆、能识别意图、能编排子 Agent**的真实可用 Agent |
| **代码能直接跑吗** | 能。每个脚本都有 `verify.sh` 一键验证 |
| **要花钱吗** | 默认用阿里云通义千问（DashScope，新用户免费额度足够走完全程） |

---

## 课程地图（4 章 · 11 个里程碑）

```
┌──────────────────────────────────────────────────────────────────┐
│  Part 1 · 理论篇                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Ch 1  Python 基础     函数 / class / 包 / venv / FastAPI        │
│  Ch 2  LangChain 基础  LLM / Prompt / Chain / Tool / Agent       │
│  Ch 3  框架对比        同一任务用三种框架实现 (LangChain /      │
│                        LangGraph / DeepAgents) — 看清差异         │
├──────────────────────────────────────────────────────────────────┤
│  Part 2 · 实战篇                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Ch 4.1  快速开始       像 Spring Boot 一样三参数启动 Agent       │
│                         + Gradio 简单 UI 对话界面                 │
│  Ch 4.2  各功能实现     ① 多层记忆 (短期/会话/长期)              │
│                         ② 意图识别 + 路由                         │
│                         ③ 工具调用 + RAG                          │
│                         ④ SubAgent 多角色编排                     │
│  Ch 4.3  总结           端到端 demo + 类比 Spring 全景图          │
└──────────────────────────────────────────────────────────────────┘
```

完整设计文档：[docs/00-课程设计.md](docs/00-课程设计.md)

---

## 30 秒上手

### 推荐路径 · 本地 Python + IDEA (Java 工程师友好)

> 像在 IntelliJ IDEA 里跑 Spring Boot 一样, 在 PyCharm 或 IntelliJ IDEA 里**右键 Run** 任意 `01_xxx.py`. Docker 只起两个中间件 (pgvector + redis), 跟你本地起 MySQL+Redis 一个意思.

```bash
# 1. clone + 配 key
git clone git@github.com:hutiefang76/hello-my-deep_agents.git
cd hello-my-deep_agents
cp .env.example .env
# 编辑 .env, 填 DASHSCOPE_API_KEY (https://bailian.console.aliyun.com 申请)

# 2. 建 venv + 装依赖 (建议 Python 3.10/3.11)
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate    # macOS / Linux
pip install -r requirements.txt

# 3. (可选) 起中间件 — Ch4.2.1 / Ch4.2.3 / Ch4.3 的 lab 才需要
make mw-up
# 验证: docker compose -f docker-compose.middleware.yml ps  → pgvector / redis healthy

# 4. 在 PyCharm / IntelliJ IDEA 里 Run lab
#    File → Open → 选仓库根目录
#    详细配置 (Python SDK / Sources Root / EnvFile 插件) 见下方完整指南
#    然后右键 Run labs/ch04-1-quickstart-ui/src/01_quickstart.py

# 5. 关中间件 (下班前)
make mw-down
```

**完整 PyCharm / IntelliJ IDEA 配置指南** (一次性 5 分钟): [docs/08-PyCharm配置指南.md](docs/08-PyCharm配置指南.md)

---

### 备选路径 · Docker 完整栈 (跨机复现 / CI 用)

> 任何电脑只要装了 [Docker](https://www.docker.com/products/docker-desktop/) (macOS / Windows / Linux), 都能一键跑. **不需要装 Python / 不需要建 venv**, 适合验证教程能跑通 / 跨机器复现 / CI.

```bash
# 1. clone + 配 key (同上)
git clone git@github.com:hutiefang76/hello-my-deep_agents.git
cd hello-my-deep_agents
cp .env.example .env

# 2. 一键启动 (首次约 5-10 分钟下载/装依赖)
make build && make up

# 3. 跑 lab (任选一个)
make run-ch09        # Ch9 L1-L5 演化对比 (最直观)
make run-e2e         # Ch4.3 端到端集大成 demo
make ui              # 浏览器开 Gradio UI: http://localhost:7861

# 4. 或者进容器手动跑
make shell
# (容器内) python labs/ch05-workflow-vs-agent/src/01_decision_tree.py

# 5. 验证全量 (16 lab 跑通, 约 20 分钟真调 LLM)
make verify-all
```

**完整 Docker 文档**: [docs/05-Docker部署指南.md](docs/05-Docker部署指南.md)

---

## Lab 列表 — 每个都能 `python xx.py` 直接跑

### Part 1 · 理论篇

| Lab 目录 | 核心内容 | 验证方式 |
|---|---|---|
| `labs/ch01-python-basics/` | Python 函数、类、模块、虚拟环境、FastAPI mini Web | `bash verify.sh` |
| `labs/ch02-langchain-basics/` | LLM 调用、Prompt 模板、LCEL 链、工具调用、ReAct Agent | `bash verify.sh` |
| `labs/ch03-frameworks-compare/` | 同一"研究问题→搜索→总结"任务的 LangChain / LangGraph / DeepAgents 三实现 | `bash verify.sh` |

### Part 2 · 实战篇

| Lab 目录 | 核心内容 | UI / 服务 |
|---|---|---|
| `labs/ch04-1-quickstart-ui/` | `create_deep_agent` 三参数启动 + Gradio 网页对话 | `http://localhost:7860` |
| `labs/ch04-2-1-memory/` | 多层记忆（messages / checkpointer / vector long-term） | CLI |
| `labs/ch04-2-2-intent/` | 意图分类 + StateGraph 条件路由 | CLI |
| `labs/ch04-2-3-tools-rag/` | 工具调用 + RAG (InMemoryVectorStore 教学版) + write_file 落盘 | CLI |
| `labs/ch10-rag-multi-retrieval/` | RAG 多路召回 (BM25 + Hybrid RRF + MultiQuery + HyDE + Reranker) | CLI |
| `labs/ch04-2-4-subagent/` | 主-子 Agent 编排（研究员/批评家/写手） | CLI |
| `labs/ch04-3-summary/` | 集大成端到端 demo + Gradio 全功能 UI | `http://localhost:7861` |

---

## 技术栈

| 类别 | 选型 | 备注 |
|---|---|---|
| **LLM** | 阿里云通义 `qwen-plus` (DashScope) | 主路径；通过 `.env` 切换可换 OpenAI 兼容 / 本地 Ollama |
| **核心框架** | `langchain` 0.3.x + `langchain-community` | LCEL 链式组合 |
| **状态机** | `langgraph` 0.2.x | StateGraph + Checkpointer |
| **Agent 脚手架** | `deepagents` (官方) | `create_deep_agent` 三参数即跑 |
| **UI** | `gradio` | 最快搭聊天界面的方式 |
| **Web** | `fastapi` + `uvicorn` | RESTful 接入 |
| **向量库** | `pgvector` (PostgreSQL) | docker-compose 一键起 |
| **记忆** | `redis` + LangGraph Checkpointer | 会话状态持久化 |
| **测试** | `pytest` | 每个 lab 配单测 |

---

## 学习路线推荐

| 你是谁 | 推荐路径 |
|---|---|
| **Java 工程师 / Spring 老兵** | Ch 1 → Ch 4.1 → Ch 2 → Ch 4.2 → Ch 3 → Ch 4.3（先用最熟的 Spring Boot 类比抓 DeepAgents，再补 Python/LangChain 基础） |
| **Python 入门 + 想做 LLM 应用** | Ch 1 → Ch 2 → Ch 3 → Ch 4.1 → Ch 4.2 → Ch 4.3（顺序学，循序渐进） |
| **已会 LangChain / 想升级到 Deep Agent** | Ch 3 → Ch 4.1 → Ch 4.2 → Ch 4.3（直接看差异和高阶能力） |

---

## 方法论双栈

本仓库的开发节奏遵循两套方法论：

- **OpenSpec**（spec-driven development）：每个 capability 先写 spec，再写代码 — `openspec/specs/`
- **Superpowers**（brainstorm → plan → execute → verify）：每个 lab 走完整流程，含 `verify.sh` 闭环验证

详细方法论文档：
- [docs/03-OpenSpec方法论.md](docs/03-OpenSpec方法论.md)
- [docs/04-Superpowers方法论.md](docs/04-Superpowers方法论.md)

---

## 思想血脉

本教程的每一章背后, 都站着 1-2 位塑造 LLM/Agent 行业的大佬 — 不是装饰, 是设计依据. 一句话索引: [Karpathy LLM OS](docs/references/big-names/01-karpathy.md) · [Lilian Weng 三件套](docs/references/big-names/02-lilian-weng.md) · [Anthropic 5 Pattern](docs/references/big-names/04-anthropic-schluntz.md) · [Andrew Ng Reflection](docs/references/big-names/05-andrew-ng.md) · [Chase Cognitive Architecture](docs/references/big-names/06-chase.md).

完整地图 + Timeline + 落地导航见 [docs/07-大佬思想全景.md](docs/07-大佬思想全景.md); 工具栈 6 大类 (LLM/编排/状态机/脚手架/向量库/Eval) 候选对比见 [docs/06-LLM应用工具栈全景.md](docs/06-LLM应用工具栈全景.md).

---

## 开发参与

提交规范：每个 lab/章节 **单独 commit**，commit message 形如：

```
feat(ch04-2-1): implement multi-layer memory (short-term / session / long-term)

- 短期记忆: messages list (window=10)
- 会话记忆: LangGraph Checkpointer + Redis
- 长期记忆: 向量库 (InMemoryVectorStore 教学版, 生产可换 PgVector)

Verify: bash labs/ch04-2-1-memory/verify.sh
        ✅ short_term_test PASSED
        ✅ session_persist_test PASSED
        ✅ long_term_recall_test PASSED
```

---

## License

MIT — 可自由用于学习、教学、企业内训。

> 整理：frank.hutiefang | 微信: hutiefang
