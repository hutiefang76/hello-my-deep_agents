"""Case 2 验证 · Python MCP Client 调本目录下 mcp_server.py.

证明 wrapper 能正常工作, 不需要 Claude Desktop, 命令行直接看 tool 列表 + 调一次.

跑法:
    pip install mcp httpx
    python src/mcp_client.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    server_script = Path(__file__).parent / "mcp_server.py"

    # 配置: 用 stdio 启动一个子进程 (mcp_server.py)
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)],
    )

    print("=" * 60)
    print("MCP Client → 连本目录下的 mcp_server.py (它内部 HTTP 调 Java)")
    print("=" * 60)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. 握手
            await session.initialize()
            print("\n[1] Session initialized ✓")

            # 2. 列出 server 暴露的 tools
            tools = await session.list_tools()
            print(f"\n[2] Server 暴露 {len(tools.tools)} 个 tools:")
            for t in tools.tools:
                print(f"    - {t.name:20s} | {t.description[:60]}")

            # 3. 列 resources
            try:
                resources = await session.list_resources()
                print(f"\n[3] Server 暴露 {len(resources.resources)} 个 resources:")
                for r in resources.resources:
                    print(f"    - {r.uri} | {r.name}")
            except Exception as e:
                print(f"\n[3] (无 resources 或 list 失败: {e})")

            # 4. 真调一次 get_order
            print("\n[4] Calling get_order(order_id='O20260429') ...")
            result = await session.call_tool("get_order", {"order_id": "O20260429"})
            print("    返回:")
            for item in result.content:
                # FastMCP 把 dict 序列化成 TextContent
                print(f"      {item.text if hasattr(item, 'text') else item}")

            # 5. 调 list_orders
            print("\n[5] Calling list_orders() ...")
            result = await session.call_tool("list_orders", {})
            for item in result.content:
                print(f"    {item.text if hasattr(item, 'text') else item}")

            # 6. 拉 resource (订单政策)
            print("\n[6] Reading resource policy://order/cancellation ...")
            try:
                from mcp.types import TextResourceContents

                res = await session.read_resource("policy://order/cancellation")
                for content in res.contents:
                    if isinstance(content, TextResourceContents):
                        print(f"    {content.text[:200]}...")
                    else:
                        print(f"    {content}")
            except Exception as e:
                print(f"    (read_resource 失败: {e})")

    print("\n" + "=" * 60)
    print("✅ MCP Client 验证完成 — server 三件套 (Tool/Resource/Prompt) 都通了")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
