# 本地三本参考教程横向对比

> 用户追加要求 #3: "原 llm_study 是否有可取之处"。本文对比电脑上已有的三本姊妹教程，为 cherry-pick 提供决策依据。

---

## 1. 对照对象

| 仓库 | 路径 | 定位 | 形式 |
|---|---|---|---|
| **llm_study** | `C:/Users/Administrator/IdeaProjects/llm_study/` | 你自己的"理论笔记仓" | 16 课 Markdown + PDF |
| **hello-agents** | `C:/Users/Administrator/IdeaProjects/hello-agents/` | "datawhale 派"系统教材 | 16 章 + 9 扩展，理论+代码 |
| **all-in-rag** | `C:/Users/Administrator/IdeaProjects/all-in-rag/` | RAG 专题 | 9 章理论+代码 |

---

## 2. llm_study (你自己的) — 16 课全大纲

```
docs/理论/
├── 第01课-LLM原理与基础.md
├── 第02课-大模型生态.md
├── 第03课-提示词工程与结构化输出.md
├── 第04课-RAG检索增强生成.md
├── 第05课-向量数据库.md
├── 第06课-记忆系统.md
├── 第07课-工具调用.md
├── 第08课-通讯协议MCP-A2A-ANP.md       ← 本教程没有！
├── 第09课-Agent架构.md
├── 第10课-多Agent编排与工作流.md
├── 第11课-框架与技术栈.md
├── 第12课-模型部署与推理服务.md          ← 本教程没有！
├── 第13课-可观测性与评估.md              ← 本教程只 Ch8 浅提
├── 第14课-安全与Guardrails.md           ← 本教程只 Ch8 浅提
├── 第15课-合规与治理.md                 ← 本教程没有！
└── 第16课-数据处理ETL.md
```

### Cherry-pick 价值评估

| 课 | 价值 | 决策 |
|---|---|---|
| 01 LLM 原理 | ⭐⭐ 太基础 | 不抄，README 一段引用即可 |
| 02 大模型生态 | ⭐⭐⭐⭐ 我们没"全景图" | **抄到 [docs/06-LLM应用工具栈全景.md](../../06-LLM应用工具栈全景.md)** |
| 03 提示词 | ⭐⭐⭐ 重叠 Ch2 | 不抄，但提取 Brockman 4 段式风格 |
| 04 RAG | ⭐⭐⭐ Ch4.2.3+Ch10 已覆盖 | 不抄 |
| 05 向量库 | ⭐⭐⭐⭐ 我们只用一种 | 提取做 Ch10 附录"向量库选型" |
| 06 记忆 | ⭐⭐ Ch4.2.1+Ch8 已超过 | 不抄 |
| 07 工具调用 | ⭐⭐⭐ Ch2+Ch4.2.3+Ch8 已覆盖 | 不抄 |
| **08 MCP/A2A/ANP** | ⭐⭐⭐⭐⭐ **本教程零覆盖** | **完整 cherry-pick → 新增 Ch12** |
| 09 Agent 架构 | ⭐⭐⭐ Ch3+Ch5+Ch9 已覆盖 | 不抄 |
| 10 多 Agent 编排 | ⭐⭐⭐ Ch4.2.4 已覆盖 | 不抄 |
| 11 框架技术栈 | ⭐⭐⭐⭐ 同 02 | 合到 docs/06 全景图 |
| **12 部署** | ⭐⭐⭐⭐ 本教程无 | P3 优先级，新增 Ch13 |
| **13 可观测性+评估** | ⭐⭐⭐⭐ Ch8 浅，需深化 | **完整 cherry-pick → 升级 Ch8** |
| **14 Guardrails** | ⭐⭐⭐⭐ Ch8 只一个脚本 | **cherry-pick → 升级 Ch8/03_guardrails** |
| 15 合规 | ⭐⭐⭐ 偏理论 | 概念引入即可 |
| 16 ETL | ⭐⭐ 可不抄 | 不抄 |

---

## 3. hello-agents (datawhale 派) — 16 章

```
第一部分: 智能体与语言模型基础
├── 第一章 初识智能体
├── 第二章 智能体发展史
└── 第三章 大语言模型基础

第二部分: 构建你的大语言模型智能体
├── 第四章 智能体经典范式构建 (ReAct/Plan-and-Solve/Reflection)  ← 我们 ReAct 浅
├── 第五章 基于低代码平台的智能体搭建 (Coze/Dify/n8n)             ← 不做，本教程是代码派
├── 第六章 框架开发实践 (AutoGen/AgentScope/LangGraph)            ← 我们框架对比 Ch3 仅 3 个
└── 第七章 构建你的 Agent 框架                                     ← 不做，本教程用 DeepAgents

第三部分: 高级知识扩展
├── 第八章 记忆与检索                                              ← 我们 Ch4.2.1+Ch8+Ch10 更深
├── 第九章 上下文工程                                  ★          ← **我们 P0 要新增 Ch11**
├── 第十章 智能体通信协议                              ★          ← **我们 P0 要新增 Ch12**
├── 第十一章 Agentic-RL                                            ← 不做，超出"应用工程师"定位
└── 第十二章 智能体性能评估                                        ← 我们升级 Ch8

第四部分: 综合案例进阶
├── 第十三章 智能旅行助手                                          ← 可借鉴
├── 第十四章 自动化深度研究智能体                                  ← Ch3 已有 mini 版
└── 第十五章 构建赛博小镇                                          ← 太花哨, 不做

第五部分: 毕业设计
└── 第十六章 毕业设计

扩展:
├── Extra02 上下文工程补充                  ★ 拉近 Ch11 设计
└── Extra09 Agent 应用开发踩坑              ★ 价值高
```

### Cherry-pick 价值

- **第九章 上下文工程**: 直接对应我们 P0 Ch11 — 借鉴目录设计但代码自己写
- **第十章 通信协议**: 我们 P0 Ch12 的核心参考
- **Extra02 上下文工程补充 / Extra09 踩坑分享**: P3 阶段精读, 提取常见坑位

---

## 4. all-in-rag — 9 章

```
第一章 RAG 入门
第二章 数据准备 (加载/切分)
第三章 索引构建 (向量嵌入/向量库/索引优化)
第四章 检索优化 (混合检索/查询构造/Text2SQL/查询重写)  ★★★★★  ← Ch10 最大参考
第五章 生成集成 (格式化生成)
第六章 评估与工具
第七章 KG-RAG (知识图谱 RAG)
第八章 综合项目 (食谱多模态 RAG)
第九章 GraphRAG (图谱架构/索引/智能查询路由)
```

### 第四章 检索优化 — 子目录

```
docs/chapter4/
├── 11_hybrid.md           混合检索
├── 12_text2sql.md         自然语言转 SQL
├── 13_advanced_retrieval.md  高级检索
├── 14_query_construction.md  查询构造
└── 15_query_rewriting.md     查询重写

code/C3/  (在第三章里)
├── 01_bge_visualized.py   BGE 可视化
├── 04_multi_milvus.py     多 Milvus 实例
├── 05_sentence_window_retrieval.py
├── 06_recursive_retrieval.py
├── work_hybrid_multimodal_search.py  ← Hybrid 实现参考
└── work_multimodal_dragon_search.py
```

### Cherry-pick 价值

**直接为 Ch10 RAG 多路召回 提供蓝本**:
- `work_hybrid_multimodal_search.py` 是混合检索的最直接参考
- `06_recursive_retrieval.py` 递归检索可作为 Ch10 进阶
- chapter4/12_text2sql / 14_query_construction / 15_query_rewriting 三篇可以作为 Ch10 的"附录扩展阅读"

---

## 5. 三仓库横向能力图

| 能力 | llm_study | hello-agents | all-in-rag | **本教程 v1** | **本教程 v2 计划** |
|---|---|---|---|---|---|
| Java→Python 类比 | ❌ | ❌ | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (Java 等价代码) |
| Workflow Patterns | ⚠️ | ⚠️ | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cognitive Architecture | — | ⚠️ | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Reflection 单章 | — | ⚠️ | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 多层记忆 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Advanced RAG** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ (Ch10) |
| **Context Engineering** | — | ⭐⭐⭐⭐ | — | ❌ | ⭐⭐⭐⭐⭐ (Ch11) |
| **MCP/A2A 协议** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | — | ❌ | ⭐⭐⭐⭐ (Ch12) |
| 评估/可观测性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ (Ch8 升级) |
| Guardrails | ⭐⭐⭐⭐ | — | — | ⭐⭐ | ⭐⭐⭐⭐ (Ch8 升级) |
| 部署 | ⭐⭐⭐⭐ | — | — | — | ⭐⭐⭐ (Ch13) |
| Spring 类比 | — | — | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 6. 结论 — Cherry-pick 行动清单

**P0 (必须做)**:
- [ ] 从 [llm_study/理论/第08课-通讯协议MCP-A2A-ANP.md](C:/Users/Administrator/IdeaProjects/llm_study/理论/第08课-通讯协议MCP-A2A-ANP.md) 提取 → 新建 Ch12 MCP
- [ ] 从 [all-in-rag/code/C3/work_hybrid_multimodal_search.py](C:/Users/Administrator/IdeaProjects/all-in-rag/code/C3/work_hybrid_multimodal_search.py) 提取 → Ch10 hybrid 实现参考
- [ ] 从 [hello-agents/docs/chapter9 上下文工程](C:/Users/Administrator/IdeaProjects/hello-agents/docs/chapter9/) 提取设计灵感 → Ch11

**P1 (高优)**:
- [ ] llm_study 第02课 大模型生态 → docs/06-LLM应用工具栈全景图
- [ ] llm_study 第13课 可观测性 + 第14课 Guardrails → 升级 Ch8

**P2 (中优)**:
- [ ] llm_study 第12课 部署 → 新增 Ch13 部署章
- [ ] hello-agents Extra02/Extra09 踩坑分享 → 课程总结的"避坑清单"

**Cherry-pick 原则**:
1. 不抄代码——只抄结构和概念
2. 抄前必读懂、解构、重写——避免技术债
3. 引用必标 [docs/references/...](../) 索引
