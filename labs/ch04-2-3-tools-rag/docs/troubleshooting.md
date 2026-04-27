# 故障排查手册

## LLM 调用相关

### 问题: DASHSCOPE_API_KEY 报 invalid

- 检查 .env 是否存在
- 检查 key 是否以 sk- 开头, 长度约 32 字符
- 控制台 (https://bailian.console.aliyun.com) 看额度是否用完
- 检查机器时间是否同步 (DashScope 拒绝大幅时差请求)

### 问题: 调用很慢 / 超时

- 默认超时 30s, 可在 ChatTongyi 构造时调 timeout=60
- 网络问题: ping dashscope.aliyuncs.com
- qwen-plus 平均 1-3s, qwen-max 3-8s, 选择更快的模型
- 流式调用 (streaming=True) 体验更好但总耗时不变

### 问题: token 超限 (max_tokens / context_window)

- qwen-plus 上下文 32k, qwen-max 32k, qwen-long 1M
- messages 太长: 用窗口截断 / Checkpointer 总结
- 单次响应太长: 设 max_tokens 限制

## 向量库相关

### 问题: PgVector 装不上

- 用 docker-compose 起 pgvector/pgvector:pg16 镜像 (推荐)
- 不用 docker: PostgreSQL 16 + apt-get install postgresql-16-pgvector
- 教学场景用 InMemoryVectorStore (langchain-core 内置, 不依赖 PG)

### 问题: 检索不准

- 检查 chunk_size: 太小 (<200) 没语义, 太大 (>1500) 噪音
- 检查 chunk_overlap: 一般是 chunk_size 的 10-20%
- 检查 embedding 模型: 中文场景必须用支持中文的 (text-embedding-v3 / bge-large-zh)
- 引入 reranker (BGE Reranker / Cohere Rerank) 二次精排

## DeepAgents 相关

### 问题: Agent 不停循环, recursion_limit 报错

- 默认 recursion_limit=25, 调高: config={"recursion_limit": 50}
- 检查 system_prompt: 是否明确告诉 Agent 何时停止
- 工具描述要清晰, 避免 Agent 误判工具结果

### 问题: SubAgent 不工作

- 检查 deepagents 版本 >= 0.5
- 检查 subagents=[...] 参数格式 (是 SubAgent 对象不是字符串)
- 看 result['messages'] 中是否有 task tool 调用

### 问题: virtual file system 文件丢了

- files 在 result['files'] 里, 不是真实文件系统
- 跨 invoke 持久化必须用 Checkpointer (thread_id 一致)
- 想真实落盘: 自己写一个 save_to_disk 工具
