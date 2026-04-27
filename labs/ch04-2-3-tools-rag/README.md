# Ch 4.2.3 · 工具调用 + RAG

> Agent 的两大业务能力: 调你的代码 (工具) + 查你的知识库 (RAG).

## 学完能力

- 写复杂的自定义工具 (多参数、Pydantic 返回类型、异常处理)
- 跑通完整的 RAG pipeline (文档加载→切分→向量化→检索→增强生成)
- 把 RAG 包装成工具给 DeepAgent 用 (Agent 可以决定何时查知识库)

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_custom_tool.py` | 自定义工具进阶 (Pydantic 入参/返回, 异常, 流式) | `python src/01_custom_tool.py` |
| `02_rag_pipeline.py` | 完整 RAG pipeline (从 .md 文档到检索回答) | `python src/02_rag_pipeline.py` |
| `03_deepagent_with_rag.py` | 把 RAG 包成工具给 DeepAgent | `python src/03_deepagent_with_rag.py` |

## 数据源

`docs/` 目录里有 3 篇示例文档 (markdown):
- `product_faq.md`     产品 FAQ
- `tech_stack.md`      技术栈说明
- `troubleshooting.md` 故障排查

跑 02/03 时这些文档会被加载、切分、向量化, 存到 InMemoryVectorStore.

## 一键验证

```bash
bash verify.sh
```

## 关键代码片段

### 复杂自定义工具
```python
from pydantic import BaseModel
from langchain_core.tools import tool

class OrderArgs(BaseModel):
    order_id: str = Field(description="订单 ID, 如 O20260427")
    fields: list[str] = Field(default=["status"], description="要查的字段")

@tool(args_schema=OrderArgs)
def query_order_v2(order_id: str, fields: list[str]) -> dict:
    """查询订单 (复杂入参版本)."""
    ...
```

### RAG pipeline
```python
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from common.llm import get_embeddings

# 1. 加载 + 切分
docs = TextLoader("docs/product_faq.md").load()
chunks = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

# 2. 向量化 + 入库
vs = InMemoryVectorStore(get_embeddings())
vs.add_documents(chunks)

# 3. 检索
results = vs.similarity_search("退货政策", k=3)
```

### RAG 包装成工具给 DeepAgent
```python
@tool
def search_kb(query: str, k: int = 3) -> str:
    """检索内部知识库."""
    docs = vs.similarity_search(query, k=k)
    return "\n\n".join(d.page_content for d in docs)

agent = create_deep_agent(model, tools=[search_kb], system_prompt=...)
```

## 下一步

学完工具+RAG → 进 [Ch 4.2.4 SubAgent 编排](../ch04-2-4-subagent/) 让 Agent 派子任务给专家.
