"""Case 2 · Python MCP Server 包装现有 Java REST 服务.

场景: Java 服务不能动 (legacy / 不在你团队), 但你要让 LLM Agent 用上它.
解法: Python 写一层 MCP server, 内部 HTTP 调 Java REST. LLM 看到的是 MCP, 实际执行的是 Java.

架构:
    LLM Agent (Claude/Cursor) ──MCP──> Python MCP Server ──HTTP──> Java SpringBoot REST
                                       (本文件)                    (legacy 不动它)

为什么用 mcp 官方 Python SDK (FastMCP):
    - 跟 Spring AI 的 @Tool 注解一一对应, 心智模型一致
    - 只需 pip install mcp, 不引重型框架
    - stdio 传输 (Claude Desktop 默认) + SSE 传输 (HTTP 部署) 都支持

跑法:
    1. 先把 Case 1 的 Spring Boot 起在 :8080
       cd ../../spring-boot-mcp && mvn spring-boot:run
    2. 跑本 server (stdio 传输, 给 Claude Desktop):
       python src/mcp_server.py
       或 SSE 传输 (HTTP 部署):
       python src/mcp_server.py --sse
    3. 验证: python src/mcp_client.py

依赖: pip install mcp httpx
"""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Java REST 服务地址 (默认 Case 1 的 Spring Boot)
JAVA_BASE_URL = os.getenv("JAVA_ORDER_API", "http://localhost:8080/api/orders")
HTTP_TIMEOUT = 5.0

# 创建 MCP Server 实例
# name: 给 client 看的服务名 (Claude Desktop 列表里显示这个)
mcp = FastMCP("Java-Order-Wrapper")


@mcp.tool()
def get_order(order_id: str) -> dict[str, Any]:
    """根据订单 ID 查询订单详情.

    参数:
        order_id: 订单编号 (如 O20260429)

    返回:
        订单详情 dict (status / total / items)

    内部实现: HTTP GET 调 Java SpringBoot REST endpoint.
    """
    try:
        r = httpx.get(f"{JAVA_BASE_URL}/{order_id}", timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        return {"error": f"调 Java 服务失败: {e}", "java_url": JAVA_BASE_URL}


@mcp.tool()
def list_orders() -> list[dict[str, Any]]:
    """列出所有订单. 用于概览.

    返回:
        订单列表
    """
    try:
        r = httpx.get(JAVA_BASE_URL, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        return [{"error": f"调 Java 服务失败: {e}"}]


@mcp.tool()
def cancel_order(order_id: str) -> dict[str, Any]:
    """取消订单. 已发货的订单无法取消.

    参数:
        order_id: 要取消的订单编号

    返回:
        操作结果 (ok=True 或 error=...)
    """
    try:
        r = httpx.get(f"{JAVA_BASE_URL}/{order_id}/cancel", timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        return {"error": f"调 Java 服务失败: {e}"}


# ===== Resource (read-only 数据) 示例 =====
# Tool 是有副作用的函数, Resource 是 read-only 的数据查询. 这里用 Resource 暴露订单政策.

@mcp.resource("policy://order/cancellation")
def order_cancel_policy() -> str:
    """暴露订单取消政策 (LLM 可拉取作为上下文).

    URI: policy://order/cancellation
    """
    return """
    订单取消政策 (v2.3):
    - 处理中订单: 可任意取消
    - 已发货订单: 不可取消, 客户需走"申请退货"
    - 已签收订单: 不可取消, 客户需走"7 天无理由退货"
    """


# ===== Prompt 模板示例 =====
# Prompt 是可复用的提示词模板. LLM Client 可拉取后填值.

@mcp.prompt()
def order_inquiry_prompt(order_id: str) -> str:
    """订单咨询的标准 prompt 模板.

    参数:
        order_id: 客户咨询的订单 ID
    """
    return f"""你是订单客服. 客户咨询订单 {order_id} 的情况.
请按以下步骤操作:
1. 用 get_order 工具查订单状态
2. 如客户要取消, 先查 policy://order/cancellation 政策
3. 如政策允许取消, 用 cancel_order 工具
4. 用 simply 中文回复客户"""


def main() -> None:
    """启动 MCP server. 默认 stdio 传输 (给 Claude Desktop)."""
    # 强制 UTF-8 stdout (Windows GBK 终端兼容)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # 检查 Java 服务是否可达 (友好提示)
    try:
        httpx.get(f"{JAVA_BASE_URL}", timeout=2)
        print(f"[INFO] Java 服务可达: {JAVA_BASE_URL}", file=sys.stderr)
    except Exception:
        print(
            f"[WARN] Java 服务不可达 ({JAVA_BASE_URL}). "
            f"请先在 ../spring-boot-mcp/ 跑 mvn spring-boot:run",
            file=sys.stderr,
        )

    # 启动方式:
    # 默认 stdio (Claude Desktop / Cursor): mcp.run(transport="stdio")
    # SSE (HTTP 部署): mcp.run(transport="sse")
    transport = "sse" if "--sse" in sys.argv else "stdio"
    print(f"[INFO] MCP Server 启动 (transport={transport})", file=sys.stderr)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
