# Spec: llm-provider-abstraction

> 共享 LLM 工厂, 让所有 lab 能切换 provider 不改代码.

**Status**: Implemented (Commit #1)
**Capability owner**: `common/llm.py`
**Related lab**: 全部 lab

## Why

学员只配一次 `.env`, 全部 lab 直接跑. 切换不同 LLM provider (云端通义 / OpenAI 兼容 / 本地 Ollama) = 改一行 .env, 不动代码.

## Requirements

### Must

1. **M1**: 提供 `get_llm()` 函数, 默认从 `.env` 读 `LLM_PROVIDER` / `LLM_MODEL` / `LLM_TEMPERATURE`
2. **M2**: 支持三种 provider:
   - `tongyi`: 用 `ChatTongyi` (langchain-community) + `DASHSCOPE_API_KEY`
   - `openai_compat`: 用 `ChatOpenAI` (langchain-openai) + `OPENAI_API_KEY` + `OPENAI_BASE_URL`
   - `ollama`: 用 `ChatOllama` (langchain-ollama) + `OLLAMA_BASE_URL`
3. **M3**: 函数参数可覆盖 .env 设置 (`get_llm(model="qwen-max")`)
4. **M4**: 自动从仓库根加载 `.env` (向上找 5 层, 容错 lab 嵌套)
5. **M5**: 占位符 key (`sk-xxx*`) 拒绝调用并报错引导申请

### Should

1. **S1**: `lru_cache` 缓存 LLM 实例, 同参数不重复构造
2. **S2**: 提供 `get_embeddings()` 同等抽象
3. **S3**: `python -m common.llm` 自检入口, 验证调用通

### Could

1. **C1**: 支持 LangSmith 自动 tracing (LANGSMITH_TRACING=true)
2. **C2**: 支持模型路由 (按任务类型自动选 qwen-plus / qwen-max)
3. **C3**: 失败重试 + 退避 (用 tenacity)

## Verification

```bash
# 自检
python -m common.llm

# 切换 provider 测试
LLM_PROVIDER=tongyi python -m common.llm
LLM_PROVIDER=openai_compat python -m common.llm
```

预期: 输出 `LLM 调用结果 OK: xxx...`

## Implementation Notes

- 文件位置: `common/llm.py`
- `_load_env_once()` 向上找 .env, 解决 sub-agent 进 lab 子目录后找不到 env 的问题
- `lru_cache(maxsize=8)` 容纳常见 provider × model 组合
- `_build_*()` 私有函数封装具体 provider 的初始化, 单一职责

## Related Decisions

- 为什么不用 `init_chat_model()`: deepagents 文档推荐用, 但它不支持 dashscope provider, 所以仍走 ChatTongyi 直接构造
- 为什么默认 `qwen-plus` 不是 `qwen-max`: plus 性价比更好, 教学场景足够
