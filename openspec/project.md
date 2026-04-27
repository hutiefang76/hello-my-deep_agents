# Project — hello-my-deep_agents

> OpenSpec 项目宪章 · 项目级"为什么/做什么/不做什么"的单一真理源

## 1. Mission（使命）

让有 Java/Spring 背景的工程师 **3-4 周内** 用 Python + LangChain + DeepAgents 独立交付**一个真实可用的、有规划/有记忆/能识别意图/能调工具/能编排子 Agent**的智能体。

## 2. Tenets（信条）

按重要性降序，决策冲突时顶部覆盖底部：

1. **真实可执行** — 每个脚本都能 `python xx.py` 直接跑通；`verify.sh` 必须真实跑过
2. **教学优先** — 简洁 > 完备；可读 > 抽象；先跑通再优化
3. **小步快跑** — 每个里程碑单独 commit；commit message 含验证证据
4. **零密钥泄漏** — `.env` 必须在 `.gitignore`；任何明文 key 不进 commit / 文档 / log
5. **方法论双栈** — OpenSpec（spec-driven）+ Superpowers（brainstorm→plan→exec→verify）

## 3. In Scope（做什么）

- Python 基础（针对 Java 工程师快速上手）
- LangChain 0.3.x 核心 API（LLM / Prompt / LCEL / Tool / Agent）
- 框架对比（LangChain vs LangGraph vs DeepAgents）
- DeepAgents 实战（Quickstart UI / 多层记忆 / 意图识别 / 工具+RAG / SubAgent / 端到端 demo）
- 阿里云通义 DashScope 接入（主路径）+ OpenAI 兼容备选 + Ollama 本地备选
- pgvector + redis 中间件（仅 Memory/RAG lab 用）
- Gradio 网页对话 UI

## 4. Out of Scope（不做什么）

- ❌ Java / Spring AI 实现（用户明确要求 Python only）
- ❌ 模型训练 / 微调 / RLHF（属另一课程）
- ❌ Kubernetes / 大规模部署（仅做单机 + Docker）
- ❌ 移动端 SDK / 客户端（仅做 Web UI + CLI）
- ❌ 其他厂商深度集成（OpenAI/Anthropic/Google 仅作为兼容协议演示）

## 5. Stack（技术栈锁定）

| 层 | 选型 | 锁版本 |
|---|---|---|
| Python | 3.10+ | 不低于 3.10 |
| LLM 框架 | langchain | `>=0.3.0,<0.4.0` |
| 状态机 | langgraph | `>=0.2.50` |
| Agent 脚手架 | deepagents | `>=0.0.7` |
| LLM SDK | dashscope | `>=1.20.0` |
| 向量库 | pgvector | PG 16 |
| 会话存储 | redis | 7-alpine |
| Web/UI | fastapi + gradio | `0.115+` / `5+` |
| 测试 | pytest | `>=8.3` |

依赖完整清单见 [requirements.txt](../requirements.txt)。

## 6. Architecture Principles（架构原则）

1. **单 lab 自包含** — 每个 `labs/chXX-xxx/` 目录可独立理解、独立运行、独立验证
2. **共享代码下沉到 `common/`** — LLM 工厂、Embedding 工厂等横切关注点
3. **配置外置到 `.env`** — 切换 model/provider/中间件零代码改动
4. **每脚本一职** — 一个 `.py` 文件演示一个核心概念，避免"巨石脚本"
5. **测试与示例并存** — 关键 lab 配 pytest，CI-friendly（mock LLM 调用）

## 7. Quality Gates（质量门）

任何 commit 必须满足：

- [ ] 该 commit 引入的脚本都能 `python xx.py` 跑通（mock 或真调）
- [ ] 该 lab 的 `verify.sh` 输出全绿
- [ ] commit message 含 `Verify:` 段落贴出验证输出
- [ ] 关键代码有简短中文注释（why，不是 what）
- [ ] 任何 API key 都不在 commit 内容中
- [ ] `python -m py_compile <changed_files>` 无语法错

## 8. Roadmap（11 commits）

```
Commit  范围                                       状态
─────  ──────────────────────────────────────  ────────
#1     bootstrap repo                           ✅ done
#2     openspec init + AGENTS.md                🚧 in progress
#3     ch01 Python basics (7 scripts)           ⏳
#4     ch02 LangChain basics (5 scripts)        ⏳
#5     ch03 frameworks compare (3 impls)        ⏳
#6     ch04-1 quickstart + Gradio UI            ⏳
#7     ch04-2-1 multi-layer memory              ⏳
#8     ch04-2-2 intent classify + routing       ⏳
#9     ch04-2-3 tools + RAG                     ⏳
#10    ch04-2-4 subagent orchestration          ⏳
#11    ch04-3 e2e demo + summary docs           ⏳
```

详细课程设计见 [docs/00-课程设计.md](../docs/00-课程设计.md)。

## 9. Communication（参考资源）

- LangChain 官方 docs: https://python.langchain.com
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- DeepAgents docs: https://docs.langchain.com/oss/python/deepagents/overview
- DashScope 控制台: https://bailian.console.aliyun.com
- ChatTongyi 集成: https://docs.langchain.com/oss/python/integrations/chat/tongyi
- OpenSpec docs: https://openspec.dev

## 10. Owner

- 项目所有者：frank.hutiefang
- 教学风格：理论 + 实战双栈，参照 llm_study 仓库
