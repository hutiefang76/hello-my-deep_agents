# 版本发布日志

> 历史版本变更 — 用于 RAG 测试同义词/释义场景: "新功能" "改进" "bug 修复" "废弃" 等近义词的语义召回是 dense 向量的强项.

## v2.6.0 (2026-04-15) — 多路召回大版本

新增功能:
- 全新混合检索引擎 BM25 + 向量 + RRF 融合, 默认 top-10 召回提升约 25%
- 引入 BGE Reranker 二次精排, 端到端 Recall@5 从 78% 提升到 92%
- 支持 MultiQuery 自动改写, 复杂提问命中率提升明显
- 支持 HyDE (假设文档) 检索, 适合事实性问答
- LangSmith trace 全链路接入, 调用链清晰可见

改进:
- 文档切分由按字符改为按 Markdown 标题, chunk 语义更完整
- Embedding 模型从 text-embedding-v2 升级到 v3, 维度 1024 更精细
- 向量库支持热更新, 不再需要重启服务

修复:
- 修复 Streaming 模式下 token 用量统计漂移
- 修复在 Windows 路径包含中文时 TextLoader 编码异常
- 修复连续多次重试触发限流后未退避的问题

废弃:
- 不再推荐 InMemoryVectorStore 用于生产环境, 请改用 PgVector / Milvus
- 废弃 v1 检索 API, 请迁移到 /api/v2/retrieve

## v2.5.0 (2026-02-20) — 工作流模式版本

新功能:
- 引入 Anthropic 5 工作流模式 (Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer)
- Reflection 模式落地, Andrew Ng 4 patterns 全部覆盖
- Cognitive Architecture L1-L5 演化路径文档化

改进:
- DeepAgents 升级到 0.5, 支持 SubAgent 显式声明
- LangGraph Checkpointer 支持 SQLite 后端, 适合中小团队

## v2.4.0 (2025-12-10) — Memory 多层化

新功能:
- 实现 Lilian Weng 三层记忆: 短期 (window) / 长期 (vector) / 工作记忆 (scratchpad)
- 支持 OpenAI 4 类记忆: episodic / semantic / procedural / persona
- 引入 Mem0 兼容层

修复:
- 修复 Redis 会话记忆超时未清理
- 修复 PostgreSQL pgvector 大批量入库时的事务超时

## v2.3.0 (2025-10-05) — 主流框架对齐

新功能:
- 支持 LangChain / LangGraph / DeepAgents 三种风格切换
- 支持本地 Ollama qwen2.5:7b 离线模式

废弃:
- 废弃 Anthropic SDK 1.x 调用, 请升级到 1.5+

## v2.2.0 (2025-08-12) — 基础 RAG

新功能:
- 接入 DashScope embedding text-embedding-v2
- 接入 PgVector / Milvus
- 提供文档加载 / 切分 / 入库 / 检索全流程示例

## v2.1.0 (2025-06-30) — 工具调用

新功能:
- 引入 Pydantic 入参 / 返回的强类型工具
- 支持 streaming 工具响应
- 异常自动重试三次后再回报模型

## v2.0.0 (2025-04-15) — 大版本重构

新功能:
- 切到 LangChain 0.3, 接入 LCEL
- 全面拥抱 ChatMessageHistory + RunnableWithMessageHistory
- 暴露 OpenAI 兼容协议 API

破坏性变更:
- 从单体改为模块化, common/llm.py 工厂统一出 LLM 实例
- 配置文件从 ini 改为 .env
