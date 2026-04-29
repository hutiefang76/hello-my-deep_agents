# Case 2 · Python MCP Server 包装现有 Java REST 服务

> **场景**: Java 服务不能改 (legacy / 不在你团队), 但你要让 LLM Agent 用上它.
> **解法**: Python 写一层 MCP server, 内部 HTTP 调 Java REST. LLM 看到的是 MCP 协议, 实际执行的是 Java 业务代码.

## 架构图

```
LLM Agent (Claude/Cursor)
        │
        │ MCP 协议 (stdio 或 SSE)
        ▼
┌──────────────────────────────────┐
│  Python MCP Server (本目录)       │
│  src/mcp_server.py                │
│   - @mcp.tool() get_order(...)    │
│   - @mcp.tool() list_orders()     │
│   - @mcp.resource(...) 政策       │
│   - @mcp.prompt(...) 模板          │
└────────────┬─────────────────────┘
             │ HTTP (httpx)
             ▼
┌──────────────────────────────────┐
│  Java SpringBoot REST (legacy)    │
│  Case 1 的 OrderService           │
│  http://localhost:8080/api/orders │
└──────────────────────────────────┘
```

## 关键 API (FastMCP)

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Java-Order-Wrapper")

@mcp.tool()                              # 等价 Spring AI 的 @Tool
def get_order(order_id: str) -> dict:
    """根据订单 ID 查订单状态."""
    r = httpx.get(f"http://localhost:8080/api/orders/{order_id}")
    return r.json()

@mcp.resource("policy://order/cancellation")  # read-only 数据
def order_cancel_policy() -> str:
    return "处理中订单可取消, 已发货不可取消..."

@mcp.prompt()                            # 复用 prompt 模板
def order_inquiry_prompt(order_id: str) -> str:
    return f"你是客服... 查询订单 {order_id}..."

mcp.run()  # 默认 stdio
```

## 跑法

### 一键 (本仓库根 .venv 已装)

```bash
# 1. 装依赖 (首次)
pip install -r requirements.txt
# 或: ../../.venv/Scripts/python.exe -m pip install -r requirements.txt  (Win)

# 2. 起 Java 服务 (Case 1)
cd ../spring-boot-mcp
mvn spring-boot:run    # 起在 :8080

# 3. 起 Python wrapper (新 terminal)
cd ../python-wrapper
python src/mcp_server.py            # stdio (给 Claude Desktop)
# 或:
python src/mcp_server.py --sse      # SSE (HTTP 部署)

# 4. 验证 (新 terminal)
python src/mcp_client.py
```

### 在 Claude Desktop 接 wrapper

`%APPDATA%\Claude\claude_desktop_config.json` (Win) 或 `~/Library/Application Support/Claude/claude_desktop_config.json` (mac):

```json
{
  "mcpServers": {
    "java-order-wrapper": {
      "command": "python",
      "args": ["C:\\path\\to\\labs\\ch12-mcp-a2a\\python-wrapper\\src\\mcp_server.py"],
      "env": {
        "JAVA_ORDER_API": "http://localhost:8080/api/orders"
      }
    }
  }
}
```

重启 Claude Desktop, 跟 Claude 说 "查 O20260429 订单状态" — 它会:
1. 自动选 `get_order` tool (描述匹配)
2. 调 Python wrapper, wrapper HTTP 调 Java
3. 拿到结果, 用中文回你

## 何时用 Python wrapper 而不是直接 Spring AI?

| 场景 | 选 |
|---|---|
| Java 服务能改 + 团队都用 Java | **Case 1 直接 Spring AI** (零 wrapper, 性能好) |
| Java 是 legacy 不能动 | **Case 2 Python wrapper** ✅ |
| 公司 Python 工程师比 Java 多 | **Case 2** (Python 更易维护) |
| 多个 Java 服务要打包成一个 MCP server | **Case 2** (聚合层) |
| 需要在 wrapper 加 cache / rate-limit / metric | **Case 2** (Python 写中间件简单) |

## 验证产物 (`mcp_client.py` 输出示例)

```
[1] Session initialized ✓

[2] Server 暴露 3 个 tools:
    - get_order            | 根据订单 ID 查询订单详情
    - list_orders          | 列出所有订单
    - cancel_order         | 取消订单. 已发货的订单无法取消

[3] Server 暴露 1 个 resources:
    - policy://order/cancellation | order_cancel_policy

[4] Calling get_order(order_id='O20260429') ...
    {'id': 'O20260429', 'status': '已发货', 'total': 299.0, 'items': 3}

[5] Calling list_orders() ...
    [{'id': 'O20260429', ...}, ...]

[6] Reading resource policy://order/cancellation ...
    订单取消政策 (v2.3): 处理中订单: 可任意取消...

✅ MCP Client 验证完成 — server 三件套 (Tool/Resource/Prompt) 都通了
```

## 参考

- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP 文档](https://github.com/modelcontextprotocol/python-sdk#quickstart)
- [MCP 官方 spec](https://modelcontextprotocol.io/specification/2025-11-25)
