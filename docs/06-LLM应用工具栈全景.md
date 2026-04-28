# LLM 应用工具栈全景 — 6 大类 · 候选 · 我们用什么

> 给 Java 工程师的视角: LLM 应用栈像 Spring 生态, 每一层都有"门派之争". 本文按 6 大类列**至少 4 个主流候选**, 每个三段式 (解决什么 / 何时选 / 何时不选), 末尾给 Spring 类比对照表.
>
> 候选清单来源: 严格对标 [mainstream-courses.md](references/benchmarks/mainstream-courses.md) 横向对照表 + [local-references-compare.md](references/benchmarks/local-references-compare.md) 三仓库交叉验证, 不凭脑补.

---

## 全景图 (Birds Eye View)

```
┌────────────────────────────────────────────────────────────────────────┐
│  ① LLM SDK         模型直连           OpenAI · Anthropic · DashScope · Ollama
│  ② 编排框架        链路 / Prompt      LangChain · LlamaIndex · DSPy · Haystack
│  ③ Agent 状态机    流程 / Checkpoint  LangGraph · AutoGen · CrewAI · LlamaIndex Workflows
│  ④ Agent 脚手架    开箱即用           DeepAgents · Claude Code Skills · OpenAI Assistants · AgentScope
│  ⑤ 向量库          长期记忆 / RAG     pgvector · Milvus · Chroma · Qdrant · Weaviate
│  ⑥ Eval / Trace    可观测 + 评估      LangSmith · Phoenix (Arize) · Langfuse · OpenAI Evals
└────────────────────────────────────────────────────────────────────────┘
```

---

## ① LLM SDK — 模型直连层

> 解决: 怎么把"自然语言推理能力"作为 API 调进来. 越底层越靠近原始 model.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **OpenAI Python SDK** | GPT-4o / o1 / o3 / GPT-5 系列直连, 业界事实标准 | 海外业务 / 需要 o-series 推理模型 / Function Calling 最稳 | 国内合规 / 成本敏感 / 走 DashScope 兼容更省事 |
| **Anthropic Python SDK** | Claude Sonnet/Opus 直连, 长 context (200K-1M) | Code 任务 / Agent 工具调用 / 长文档分析 | 国内业务无 VPN / 不需要 200K 以上 context |
| **DashScope (阿里云通义)** | Qwen-Plus/Max/Turbo 直连 + OpenAI 兼容端点 | 国内合规 / 中文场景 / 新用户免费额度 | 跨境业务 / 需要英文 reasoning 顶配 |
| **Ollama / vLLM (自托管)** | 本地跑 Qwen/Llama/DeepSeek, 零 API 费用 | 数据不出域 / 离线 demo / 教学验证 | 生产 QPS 高 / 没 GPU / 不想运维 |
| HuggingFace Inference | 海量开源模型一站调用 | 想试小众模型 / 实验 | 主线生产 (稳定性不如商业 SDK) |

**我们用什么**: 主路径 `DashScope`, 通过 `langchain-community` 的 `ChatTongyi` 调; 备选 `ChatOpenAI` + DashScope OpenAI 兼容端点 (无缝切其他模型). 见 [labs/ch02-langchain-basics](../labs/ch02-langchain-basics/).

---

## ② 编排框架 — 链路与 Prompt 工程层

> 解决: 怎么把"调 LLM + 调工具 + 拼 prompt + 解析输出"组装成可维护的代码, 不要写一次性脚本.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **LangChain** | LCEL 链式表达 (`prompt | llm | parser`), 生态最大, integrations 最全 | 通用业务 / 需要 100+ 工具 integration / 团队已有积累 | 极简任务 (5 行代码搞定的不要上 LangChain) / 追求性能极限 |
| **LlamaIndex** | 文档/数据为中心, RAG 索引/检索 API 最丰富 | 数据密集 (PDF/SQL/Notion) 的检索增强 | 纯 Agent 流程 / 工具编排为主 |
| **DSPy** (Stanford) | 把 prompt 当"可优化参数", 用程序化 compile 替代手工调 prompt | 需要可复现实验 / 多模型对比 / 学术风格 | 业务快速交付 / 团队不熟 ML 研究范式 |
| **Haystack** | 老牌 NLP pipeline 框架, deepset 出品, RAG/QA 工业级 | 企业 RAG / NLP pipeline 偏传统 | 想要最新 Agent 能力 (Haystack 跟进慢半拍) |
| Semantic Kernel (微软) | C#/.NET 优先, 适合微软系企业 | .NET 生态深耕 | Python 团队 |

**我们用什么**: `LangChain 0.3.x` (LCEL) + 关键 RAG 用 LlamaIndex 思路 (本课程 RAG pipeline 在 ch04-2-3 用 LangChain 自带 retriever, 没引入 LlamaIndex 是为了减少依赖).

---

## ③ Agent 状态机 — 流程编排与 Checkpoint 层

> 解决: 多步、有状态、可中断恢复的 Agent 流程, 类比 Spring StateMachine + Activiti.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **LangGraph** | StateGraph + 条件边 + Checkpointer (Sqlite/Redis/Postgres) | 需要可视化状态机 / 跨次对话恢复 / Human-in-the-loop | 流程极简 (单次调用搞定) |
| **AutoGen** (微软) | 多 Agent 会话编排, "聊天驱动协作" | 多角色辩论/协作场景 / Research Agent | 单 Agent 业务 / 不想要多 Agent 通信开销 |
| **CrewAI** | "公司团队"心智 — Manager + Worker, 角色定义直观 | 学习成本敏感 / 角色化 Multi-agent | 需要细粒度状态控制 |
| **LlamaIndex Workflows** | 事件驱动 workflow, async 友好 | 已用 LlamaIndex 做 RAG, 顺手扩 workflow | 没用 LlamaIndex 的项目 |
| AgentScope (阿里) | 国内出品, 支持 Qwen 原生 + 多 Agent | 国内全栈 + 想要本土支持 | 海外团队 / 社区资料偏少 |

**我们用什么**: `LangGraph 0.2.x`. 选它的根本理由是 Harrison Chase 的 *Cognitive Architecture* 路线 (见 [大佬思想全景](07-大佬思想全景.md) → Chase). Checkpointer 用 SqliteSaver (本地) / RedisSaver (生产). 见 [labs/ch04-2-1-memory](../labs/ch04-2-1-memory/).

---

## ④ Agent 脚手架 — 开箱即用层

> 解决: 不想自己拼 Planning/Memory/Tools/SubAgent, 一行 `create_xxx_agent(model, tools, instructions)` 就启动. 类比 `@SpringBootApplication`.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **DeepAgents** (LangChain-AI) | 自动装配 4 件套: `write_todos` (Plan) + virtual FS (Memory) + SubAgent + system prompt | 需要 Plan + 长任务 + SubAgent / 想最快出 demo | 极简单任务 (杀鸡用牛刀) |
| **Claude Code / Skills** | Anthropic 官方, 文件系统原生 + Bash/Edit/Read 工具集 | Claude 优先 / Code 类任务 / 想要 Agent SDK 官方加持 | 不用 Claude / 想要框架无关 |
| **OpenAI Assistants API** | OpenAI 托管, threads/runs/files 全在 OpenAI 服务端 | OpenAI 全栈 / 不想自管状态 | 数据不出域 / 多模型策略 |
| **AgentScope** (阿里) | 国内 Multi-agent 脚手架, 支持流式/分布式 | 国内 + 多 Agent 协作 | 海外 / 单 Agent |
| smolagents (HuggingFace) | 轻量 (~1K 行), 偏向 code-act agent | 学习/试水 / 想看 Agent 内部 | 复杂生产 |

**我们用什么**: `DeepAgents` 官方 — 三参数启动, 内置 Lilian Weng 三件套 (Plan + Memory + Tool) 的工程化版本, 详见 [docs/01-DeepAgents原理.md](01-DeepAgents原理.md).

---

## ⑤ 向量库 — 长期记忆与 RAG 层

> 解决: 把 embedding 高维向量存起来, 支持近似最近邻 (ANN) 检索. 类比 Spring Data 的 Repository 但是按相似度而非精确匹配查询.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **pgvector** (PostgreSQL 扩展) | SQL 数据库一把 + 向量字段, 事务/JOIN 都还在 | 已有 PG / 数据量 < 千万级 / 想 SQL 一站搞定 | 亿级向量 / 需要专业 ANN 调参 |
| **Milvus** (Zilliz) | 工业级分布式向量库, 亿级规模 + GPU 加速 | 大数据量 / 多模态 RAG / 需要 IVF/HNSW 调参 | 数据量小 / 不想运维 K8s |
| **Chroma** | 轻量 (内嵌 / 单机 server), Python 一把跑 | 学习 / 原型 / 数据量 < 百万 | 生产 / 多副本 |
| **Qdrant** | Rust 实现, 性能好, 自带过滤 + payload | 中等规模 / 需要 metadata filter / 想要 self-host | 已用 PG (pgvector 够用) |
| **Weaviate** | GraphQL 接口, schema-first | 复杂 schema / 多模态 | 简单 KV 检索 (杀鸡用牛刀) |
| FAISS (Facebook) | 算法库不是 DB, ANN 性能基线 | 自研索引 / 算法研究 | 业务系统 (没事务/没 metadata) |

**我们用什么**: `pgvector` (docker-compose 一键起 PG+pgvector) 作主路径; `InMemoryVectorStore` 作教学最小依赖. 见 [labs/ch04-2-3-tools-rag](../labs/ch04-2-3-tools-rag/).

---

## ⑥ Eval & Observability — 评估与可观测层

> 解决: Agent 是概率系统, 你怎么知道它"今天比昨天好"? 类比 Spring Actuator + Micrometer + JUnit.

| 候选 | 解决什么 | 何时选 | 何时不选 |
|---|---|---|---|
| **LangSmith** (LangChain 官方) | Trace + Eval + Prompt Hub 三合一, 与 LangChain 零成本集成 | 已用 LangChain/LangGraph / 想最快上 trace | 不用 LangChain / 想 self-host |
| **Phoenix** (Arize, OSS) | 开源 trace + eval, OpenTelemetry 标准 | 想 self-host / 已用 OTel | 不想自运维 |
| **Langfuse** (OSS) | 开源 trace + eval + prompt 管理, self-host 友好 | 数据合规要求 / 想要 LangSmith 平替 | 没 self-host 能力 |
| **OpenAI Evals** | OpenAI 官方评估框架, 与 GPT 系列原生集成 | OpenAI 全栈 | 多模型策略 |
| Weights & Biases (Weave) | ML 实验跟踪老牌玩家, LLM 也支持 | 研究/微调任务多 | 纯应用 (太重) |
| Helicone | API 网关式可观测 (代理层 trace) | 想要"插一行 base_url" 就 trace | 需要框架级深度 trace |

**我们用什么**: 当前 [labs/ch08-engineering-pillars](../labs/ch08-engineering-pillars/) 用 `LangSmith` 路径演示 (依赖 `LANGSMITH_API_KEY`); self-host 路径在 P0 工具栈缺口 — 后续可补 `Phoenix` / `Langfuse` 实战.

---

## Java 工程师视角 — Spring 类比对照表

> 学完后, 用熟悉的 Spring 名词把 6 大类一次对齐.

| 本工具栈层 | Spring 生态对位 | 类比说明 |
|---|---|---|
| ① LLM SDK | JDBC Driver | 直连"模型数据库", API/SDK 是 driver |
| ② 编排框架 (LangChain/LCEL) | Spring Core + Bean 装配 | 把组件用声明式拼起来 |
| ③ Agent 状态机 (LangGraph) | Spring StateMachine + Activiti | 流程编排 + Checkpoint 持久化 |
| ④ Agent 脚手架 (DeepAgents) | Spring Boot Starter (`@SpringBootApplication`) | 开箱装配, 屏蔽底层 |
| ⑤ 向量库 (pgvector) | Spring Data Repository | 持久化层抽象, 不过查询语义是相似度 |
| ⑥ Eval / Trace (LangSmith) | Spring Actuator + Micrometer + JUnit | 可观测 + 健康检查 + 自动化测试 |

**关键差异**: Spring 那一套是**确定性系统**, LLM 这一套是**概率系统**——所以 Eval 层不是可选项, 是生产红线.

---

## 我们的选型一句话决策

```
LLM:        DashScope (qwen-plus)            国内 + 中文 + 免费额度
编排:       LangChain 0.3.x (LCEL)            生态最大 + Python 主流
状态机:     LangGraph 0.2.x                   Chase 路线 + Checkpointer
脚手架:     DeepAgents (官方)                 Lilian Weng 三件套工程化
向量库:     pgvector (主) + InMemory (教学)   SQL 一站 + 零依赖入门
Eval:       LangSmith (商) -> Phoenix/Langfuse (P0 待补 self-host)
```

如何决定换栈: 见 [Chase: Own Architecture, Outsource Infrastructure](references/big-names/06-chase.md) — **认知架构是护城河, 框架是 commodity**, 6 大类全部可换, 不绑定我们.

---

## 参考

- [docs/references/benchmarks/mainstream-courses.md](references/benchmarks/mainstream-courses.md) — 5 套主流课程横向对照
- [docs/references/benchmarks/local-references-compare.md](references/benchmarks/local-references-compare.md) — 本地 3 仓库 cherry-pick 表
- [docs/01-DeepAgents原理.md](01-DeepAgents原理.md) — DeepAgents 4 件套 Spring Boot 类比
- [docs/07-大佬思想全景.md](07-大佬思想全景.md) — 谁在塑造这些工具的设计哲学
