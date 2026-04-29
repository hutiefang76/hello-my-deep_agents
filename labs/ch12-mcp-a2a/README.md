# Ch 12 · MCP + A2A — 协议层让 Agent 真正生态化

> **主线对应**: 从"自己写 Agent 调自己写的工具"→ "**任何 Agent 调任何工具, 任何 Agent 调任何 Agent**"
>
> **大佬出处**:
> - **MCP** (Model Context Protocol) — Anthropic 2024-11, "USB-C for AI"
> - **A2A** (Agent-to-Agent) — Google 2025-04, "HTTP for Agents"

---

## 一句话定位

```
Ch1-Ch10:  你的 Agent 调你写的工具                    (单机版)
Ch11:       你的 Agent 用对的 Context 调对的工具       (软件工程版)
Ch12 (本章): 你的 Agent 调【全世界】的工具/Agent       (协议生态版) ← 在这
```

---

## 1. MCP vs A2A 一图分清

| 维度 | MCP (Model Context Protocol) | A2A (Agent-to-Agent) |
|---|---|---|
| 解决什么 | **LLM ↔ 工具/数据** | **Agent ↔ Agent** |
| 推出方 | Anthropic | Google |
| 时间 | 2024-11 | 2025-04 |
| 类比 | USB-C for AI | HTTP for Agents |
| 通信 | JSON-RPC over Stdio/SSE/HTTP | gRPC / HTTP + Agent Card |
| 服务端原语 | Tool / Resource / Prompt | Task / Message / Artifact |
| 谁是服务方 | MCP Server (工具方) | 任意 A2A Agent (双向对等) |
| 关系 | **互补 — 同一个项目可同时用两个** | |

```
                    ┌─────────────────────────────┐
                    │     用户的 LLM Agent         │
                    │     (Claude Desktop /        │
                    │      Cursor / 你写的)        │
                    └────┬─────────────┬───────────┘
                         │             │
                  MCP    │             │   A2A
                  ↓ 调工具/数据         ↓ 调其他 Agent
                  ↓                    ↓
        ┌────────────────────┐   ┌────────────────────┐
        │ MCP Server         │   │ Other Agent        │
        │ (本章 case 1+2)     │   │ (本章 case 3)      │
        │                    │   │                    │
        │ tools:             │   │ Agent Card:        │
        │  - getOrder()      │   │  /.well-known/     │
        │  - listProducts()  │   │   agent-card.json  │
        │ resources:         │   │ Tasks: 提交/查询    │
        │  - file://policy   │   │ Messages: 对话     │
        └────────────────────┘   └────────────────────┘
```

---

## 2. MCP 三原语

| 原语 | 用途 | 等价物 |
|---|---|---|
| **Tool** | LLM 主动调函数 (有 side effect) | OpenAI function calling / `@tool` |
| **Resource** | LLM 读数据 (read-only URI) | REST GET endpoint |
| **Prompt** | 复用 prompt 模板 | Spring Bean 的 prompt 版 |

---

## 3. A2A 协议核心

| 概念 | 含义 |
|---|---|
| **Agent Card** | `/.well-known/agent-card.json` 公开自身身份/能力 (类似 OAuth 的 well-known) |
| **Task** | 一次工作请求, 有 lifecycle (submitted → working → completed) |
| **Message** | Agent 之间往来消息, 含 parts (text/file/image) |
| **Artifact** | Task 产出物 |

---

## 4. 本章三大案例 (`src/` 全在子目录)

| Case | 路径 | 你能学到 |
|---|---|---|
| **1. Spring Boot → MCP Server** | `spring-boot-mcp/` | Java 工程师视角: 把现有 SpringBoot Service `@Tool` 注解一秒变 MCP Server |
| **2. Python 包装 Java 服务** | `python-wrapper/` | Python `mcp` SDK 包装 Java REST API, 让不会改 Java 的也能上车 |
| **3. A2A 协议 demo** | `a2a-demo/` | Python 写 Agent Card + Task server, 演示 Agent 互通 |

---

## 5. 各 Case 速览

### Case 1 · Spring Boot MCP Server (Java)

```java
// 一个普通 SpringBoot Service, 加 @Tool 注解就成了 MCP Server 暴露的工具
@Service
public class OrderService {
    @Tool(description = "根据订单 ID 查询订单状态")
    public String getOrder(@ToolParam(description = "订单 ID") String orderId) {
        // 调你原来的业务代码
        return "订单 " + orderId + " 状态: 已发货";
    }
}
```

跑法 (假设有 JDK 17+ + Maven):
```bash
cd spring-boot-mcp && mvn spring-boot:run
# MCP Server 会通过 stdio 传输, 也支持 SSE on http://localhost:8080/mcp
```

### Case 2 · Python 包装 Java 服务成 MCP

适合**没法动 Java 代码**但需要让 LLM 用上现有 Java 服务的场景:

```python
# python-wrapper/src/mcp_server.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Java-Order-Wrapper")
JAVA_URL = "http://localhost:8080/api/orders"  # 你现有 Java REST 服务

@mcp.tool()
def get_order(order_id: str) -> str:
    """根据订单 ID 查询 (内部 HTTP 调 Java 服务)."""
    r = httpx.get(f"{JAVA_URL}/{order_id}", timeout=5)
    r.raise_for_status()
    return r.json()
```

跑法:
```bash
cd python-wrapper && python src/mcp_server.py
# 或 Claude Desktop 配置里加这个 server
```

### Case 3 · A2A 协议 Demo

```python
# a2a-demo/src/agent_server.py — 一个 Agent 公开自己的 Card
@app.get("/.well-known/agent-card.json")
def agent_card():
    return {
        "name": "Research Agent",
        "version": "0.1.0",
        "capabilities": ["web_search", "summarize"],
        "endpoint": "http://localhost:9000/a2a"
    }

@app.post("/a2a/tasks")
def submit_task(task: TaskSubmit):
    # 接 task, 处理, 返回 artifact
    ...
```

```python
# a2a-demo/src/agent_client.py — 另一个 Agent 调它
card = httpx.get("http://localhost:9000/.well-known/agent-card.json").json()
task = httpx.post(f"{card['endpoint']}/tasks", json={"message": "..."}).json()
```

---

## 6. 必读参考

- [MCP 2025-11-25 spec](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Java SDK (Anthropic + Spring AI 维护)](https://github.com/modelcontextprotocol/java-sdk)
- [Spring AI MCP Boot Starter blog](https://spring.io/blog/2025/02/14/mcp-java-sdk-released-2/)
- [A2A 协议 spec](https://a2a-protocol.org/latest/specification/)
- [a2aproject/A2A GitHub](https://github.com/a2aproject/A2A)
- [Google A2A 官宣 blog (2025-04)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

---

## 7. 一键验证

```bash
bash verify.sh
```

会做:
1. 检查 Java + Maven (如果有, 编译 spring-boot-mcp)
2. 装 Python `mcp` + `a2a` SDK
3. 起 Java MCP server (后台), Python wrapper 调它
4. 起 A2A demo, client 调 server
5. 输出三个 case 的验证表

---

## 8. 何时选哪个协议

| 场景 | 推荐 |
|---|---|
| 给现有 SpringBoot 业务加 LLM 入口 | **MCP** (Case 1, Java SDK) |
| 现有 Java 服务不能改, 但想让 LLM 用 | **MCP** (Case 2, Python wrap) |
| 多个 Agent (你的+合作伙伴的) 互通 | **A2A** (Case 3) |
| 同时需要 (LLM 调工具 + Agent 间协作) | **MCP + A2A 联用** |

---

## 9. 下一步

- 把你公司的某个 SpringBoot 服务跑通 MCP Case 1
- 用 Claude Desktop config 接 MCP server (产线集成)
- 用 LangGraph 做 A2A Client 调外部 Agent

> **本章定位**: 协议是 Agent 走出"私人脚本"进入"产业协作"的入场券. **2026 年没接 MCP/A2A 的项目, 等于没接 RESTful 的 2010 年项目**.
