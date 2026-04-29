# Case 3 · A2A 协议 Demo (Agent Card + Task + Artifact)

> **场景**: 你的 Agent 想调用合作伙伴 / 第三方 / 兄弟团队的 Agent. A2A 是 "HTTP for Agents".
> **解法**: 任意 Agent 通过 `/.well-known/agent-card.json` 公开身份, 通过 `POST /a2a/v1/tasks` 接活.

## A2A 协议四步流程

```
Agent A (Client)                                Agent B (Server)
=============================================================
GET /.well-known/agent-card.json   ──────────►  返回 Agent Card
                                                (name, skills, endpoint)
                                                
看 skills 是否匹配                              
                                                
POST /a2a/v1/tasks                 ──────────►  接 Task, 处理
{ message: {parts: [...]} }                     返回 Task (含 artifacts)
                                                
                          (异步场景)             
GET /a2a/v1/tasks/{id}            ──────────►   返回当前 Task 状态
                                                (submitted/working/completed)
```

## 跑法 (一键)

```bash
# 1. 装依赖
pip install -r requirements.txt

# 2. 起 server
python src/research_agent_server.py
# 跑在 http://localhost:9000
# Agent Card: http://localhost:9000/.well-known/agent-card.json

# 3. 跑 client (新 terminal)
python src/agent_client.py
```

## 验证产物 (`agent_client.py` 输出)

```
[1] 发现 remote agent (GET /.well-known/agent-card.json)
   Agent 名称: Research Agent v0.1.0
   描述:      给 query 生成结构化研究报告
   skills:    ['research']

[2] 决策: 我需要 'research' skill, 这个 agent 有吗?
   匹配: True ✓

[3] 提交 Task: 'MCP 协议在 2026 年的发展趋势'
   Task ID:  6f7a8b9c-...
   状态:     completed
   产出物:   1 个 artifact

[4] 拿研究报告:
   --- research_report.md (text/markdown) ---
   # 研究报告: MCP 协议在 2026 年的发展趋势
   ## 关键发现
   1. MCP 协议在 2025 年成为热点
   ...

✅ A2A 协议四步走完成
   1) 发现  2) 决策  3) 提交 Task  4) 拿 artifact
```

## Agent Card 规范字段

```json
{
  "name": "Research Agent",
  "version": "0.1.0",
  "description": "...",
  "url": "http://localhost:9000",
  "capabilities": { "streaming": false, "push_notifications": false },
  "skills": [
    {
      "id": "research",
      "name": "研究查询",
      "description": "...",
      "input_modes": ["text"],
      "output_modes": ["text", "markdown"]
    }
  ]
}
```

## A2A vs MCP 何时用哪个

| 场景 | 协议 |
|---|---|
| LLM 要调"工具/数据" (DB / API / 文件) | **MCP** |
| Agent A 要调"Agent B 整套服务" | **A2A** |
| 跨公司 / 跨团队 / 跨 vendor 协作 | **A2A** (互操作性) |
| 单团队内, 给 LLM 接业务系统 | **MCP** |
| 一个项目同时用两个 | **MCP + A2A 联用** (业界主流) |

## 进阶: 接真 LLM 做研究员

`research_agent_server.py` 里的 `ResearchAgent.handle()` 现在是模板返回. 真业务里替换成:

```python
class ResearchAgent:
    def __init__(self):
        self.llm = get_llm()  # common/llm.py

    def handle(self, query: str) -> str:
        # 1. 用 Tavily 搜索
        results = tavily.search(query)
        # 2. 让 LLM 总结
        prompt = f"基于以下搜索结果写研究报告:\n{results}\n\n问题: {query}"
        return self.llm.invoke(prompt).content
```

## 参考

- [A2A 官方 spec](https://a2a-protocol.org/latest/specification/)
- [a2aproject/A2A GitHub (Python SDK)](https://github.com/a2aproject/A2A)
- [Google 官宣 blog (2025-04)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- [IBM A2A 解读](https://www.ibm.com/think/topics/agent2agent-protocol)

## 注意事项

- 本 demo 用 FastAPI + 同步处理简化展示, 真业务里 Task 通常异步 (submitted → working → completed)
- A2A 官方 Python SDK (`a2a-sdk`) 提供更完整的 streaming / push notification 实现, 本 demo 故意只用 FastAPI 让你看清协议本身
- 生产部署: 加认证 (Agent Card 可签名), 加 rate-limit, 加监控
