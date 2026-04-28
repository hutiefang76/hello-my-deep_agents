# 技术栈说明

## 后端

- 编程语言: Python 3.10+ (主力) / Java 17 (历史模块)
- Web 框架: FastAPI 0.115+ / Spring Boot 3.4 (历史)
- 数据库: PostgreSQL 16 + pgvector / Redis 7 (缓存+会话)
- 消息队列: Kafka 3.7
- 容器: Docker / Docker Compose
- 部署: Kubernetes 1.30 (生产) / 单机 docker-compose (开发)

## LLM 应用栈

- 模型: 阿里云通义 qwen-plus (主力) / OpenAI GPT-4o (备选) / Ollama qwen2.5:7b (本地)
- 框架: LangChain 0.3+ / LangGraph 0.2+ / DeepAgents 0.5+
- 向量库: PgVector (轻量) / Milvus 2.4 (亿级向量)
- Embedding: text-embedding-v3 (DashScope, 1024 维)
- UI: Gradio 5+ / 自研 React (生产)

## 数据栈

- 离线计算: Spark 3.5 / Flink 1.18
- 实时数仓: Doris 2.1
- BI: Superset
- ETL 调度: Airflow 2.10

## 监控

- APM: SkyWalking 9
- 日志: ELK (Elasticsearch + Logstash + Kibana)
- 指标: Prometheus + Grafana
- LLM 可观测性: LangSmith (开发) / 自研 trace 平台 (生产)

## 升级日历

- 2026-Q2: 从 LangChain 0.3 升 1.0
- 2026-Q3: 引入 Anthropic Claude 4.7 作为备选模型
- 2026-Q4: 把 LangSmith 替换为自研 trace 平台
