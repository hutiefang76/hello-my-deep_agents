"""03 · DeepAgents + Gradio 网页对话 UI.

把 Agent 套上一个网页界面 — 用户在浏览器输入, 看到 LLM 流式回复 + 中间步骤.

教学要点:
    - Gradio 是 Python 最快的 LLM UI 方案
    - 用 gr.ChatInterface 自动给你 history / streaming / typing indicator
    - DeepAgents 的中间状态 (todos / 文件) 也能可视化

Run:
    python 03_gradio_ui.py
    # 浏览器打开: http://localhost:7860
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "labs" / "ch03-frameworks-compare" / "src"))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

import gradio as gr  # noqa: E402
from common.llm import get_llm  # noqa: E402
from common_search import web_search  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402


SYSTEM_PROMPT = """你是一个全能助手. 根据用户问题:
- 简单问题: 直接回答
- 需要查资料: 用 web_search
- 复杂任务: 用 write_todos 列计划, 用 write_file 落笔记, 最后总结

回答要有结构: 必要时用 markdown 列表, 1-3 段."""

# 全局单例 Agent (Gradio worker 共享)
_AGENT = None


def get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = create_deep_agent(
            model=get_llm(),
            tools=[web_search],
            system_prompt=SYSTEM_PROMPT,
        )
    return _AGENT


def chat_fn(message: str, history: list) -> str:
    """Gradio ChatInterface 回调函数 — 接 message + history, 返回 reply."""
    agent = get_agent()

    # 把 history 转成 LangChain 消息格式
    # Gradio 5.x: history 是 list[dict({role, content})]
    from langchain_core.messages import AIMessage

    lc_messages = []
    for h in history:
        if isinstance(h, dict):
            role = h.get("role", "")
            content = h.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        elif isinstance(h, (list, tuple)) and len(h) == 2:
            # 老版 list[tuple(user, assistant)] 兼容
            user_msg, ai_msg = h
            if user_msg:
                lc_messages.append(HumanMessage(content=str(user_msg)))
            if ai_msg:
                lc_messages.append(AIMessage(content=str(ai_msg)))

    lc_messages.append(HumanMessage(content=message))

    try:
        result = agent.invoke(
            {"messages": lc_messages},
            config={"recursion_limit": 20},
        )
        messages = result["messages"]
        files = result.get("files", {})
        todos = result.get("todos", [])

        # 主回复
        reply = messages[-1].content if messages else "(无回复)"

        # 附加调试信息 (Agent 内部状态)
        debug_lines = []
        tool_calls_made: list[str] = []
        for m in messages:
            for tc in getattr(m, "tool_calls", []) or []:
                tool_calls_made.append(tc.get("name", ""))
        if tool_calls_made:
            debug_lines.append(f"\n\n---\n*🔧 调用工具*: {sorted(set(tool_calls_made))}")
        if todos:
            debug_lines.append(
                "\n*📋 计划*: "
                + " / ".join(f"[{t.get('status', '?')[:4]}] {t.get('content', '')[:30]}" for t in todos)
            )
        if files:
            debug_lines.append(f"\n*📁 虚拟文件*: {list(files.keys())}")

        return reply + "".join(debug_lines)

    except Exception as e:
        return f"❌ 出错: {type(e).__name__}: {e}"


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="hello-my-deep_agents · Ch4.1 Quickstart UI") as demo:
        gr.Markdown(
            """
            # 🚀 hello-my-deep_agents · Quickstart

            DeepAgents + 阿里云通义 qwen-plus + Gradio UI.

            **试试问**:
            - 你好
            - LangGraph 和 DeepAgents 有什么关系?
            - 帮我研究一下 RAG 技术, 列计划+搜资料+写笔记
            """
        )

        gr.ChatInterface(
            fn=chat_fn,
            examples=[
                "你好",
                "用一句话介绍 DeepAgents",
                "帮我研究 LangChain 和 LangGraph 的关系, 列计划+搜资料+写笔记",
            ],
        )

        gr.Markdown(
            """
            ---
            *Powered by [DeepAgents](https://github.com/langchain-ai/deepagents) ·
            阿里云通义 qwen-plus · Gradio*
            """
        )
    return demo


def main() -> None:
    print("=" * 60)
    print("Ch4.1 · 03 Gradio UI")
    print("=" * 60)
    port = int(os.getenv("GRADIO_PORT", "7860"))
    print(f"  浏览器打开: http://localhost:{port}")
    print(f"  Ctrl+C 退出")
    print("=" * 60)

    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
