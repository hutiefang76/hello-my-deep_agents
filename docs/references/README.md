# 参考资料库 · References

> 本教程审核（2026-04-28）落盘的外部参考资料。所有大佬观点、主流教程对标、RAG 进阶资料都在这里——P7 落地时**先读这里**，不用再 Google。

## 目录结构

```
docs/references/
├── README.md                      # 本文件 · 索引导览
├── big-names/                     # 大佬思想卡片（每人一份原话+核心观点+落地章节）
│   ├── 01-karpathy.md            # Andrej Karpathy · LLM OS / Software 2.0 / Context Engineering
│   ├── 02-lilian-weng.md         # Lilian Weng · LLM Agent = Plan + Mem + Tool 三件套
│   ├── 03-hassabis.md            # Demis Hassabis · DeepMind · DeepThink / AlphaGo-style search
│   ├── 04-anthropic-schluntz.md  # Schluntz & Zhang · Building Effective Agents · 5 Workflow Patterns
│   ├── 05-andrew-ng.md           # Andrew Ng · 4 Agentic Design Patterns
│   ├── 06-chase.md               # Harrison Chase · Cognitive Architecture / 5 Levels of Autonomy
│   ├── 07-brockman.md            # Greg Brockman · 4-Part Prompt Framework
│   ├── 08-altman.md              # Sam Altman · 2025-2027 Agent Roadmap
│   ├── 09-sutskever.md           # Ilya Sutskever · "Superintelligence is agentic"
│   └── 10-tobi-lutke.md          # Tobi Lütke · Context Engineering Endorsement
│
├── topics/                        # 主题深挖（针对教程缺口）
│   ├── rag-multi-retrieval.md    # RAG 多路召回 · BM25/Hybrid/MultiQuery/HyDE/Reranker
│   └── context-engineering.md    # Context Engineering 概念全景
│
└── benchmarks/                    # 对标参考
    ├── mainstream-courses.md     # 主流 LLM 课程大纲（mlabonne/DeepLearning.AI/start-llms 等）
    └── local-references-compare.md  # 本地三本教程横向对比（hello-agents/all-in-rag/llm_study）
```

## 使用约定

1. **落地章节**: 每张大佬卡片末尾必有「**落地到本教程哪一章**」段落——P7 写代码前先看
2. **原文金句**: 必有英文原句 + 中文翻译 + 出处链接，**不允许"我记得他说过"**
3. **更新规则**: 大佬出新言论 → 在对应卡片底部 append "## 更新记录" 段落，**不覆盖历史**
4. **引用规范**: 教程的 src/*.py 头部 docstring 引用大佬时，必须写 `# Ref: docs/references/big-names/01-karpathy.md`，而不是直接贴外链——**单点真相**

## 总目标对照表

| 用户原始目标 | 对应参考资料位置 |
|---|---|
| Goal 1: Java→Python 无痛 | （Java 等价代码不在 references，在 labs/ch01）|
| Goal 2: 框架做什么 | benchmarks/mainstream-courses.md |
| Goal 3: 主流覆盖 + 多层记忆/工作流/RAG多路召回 | topics/rag-multi-retrieval.md |
| Goal 4: 大佬观点既理论又实践 | big-names/ 全套 10 张卡片 |

## 增补流程

发现新大佬观点/新参考资料：
1. 先建 `.md` 落到对应子目录
2. 在本 README 索引段添加一行
3. 在相关 lab 的 README 加一行 `> Ref: docs/references/...`

> **因为信任所以简单**——参考资料的可追溯性是教程长期可维护的底层逻辑。
