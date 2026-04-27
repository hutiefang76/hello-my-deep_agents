"""02 · 全功能 Gradio UI — 端到端研究 Agent 上网页.

复用 01 的 chat() 函数, 套上 Gradio ChatInterface, 让用户在浏览器对话.

Run:
    python 02_gradio_full_ui.py
    # 浏览器打开: http://localhost:7861
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

import gradio as gr  # noqa: E402

# 复用 01 的端到端逻辑
import importlib.util as _il

_e2e_path = Path(__file__).parent / "01_e2e_research_agent.py"
_spec = _il.spec_from_file_location("e2e_module", _e2e_path)
_e2e = _il.module_from_spec(_spec)
_spec.loader.exec_module(_e2e)

chat_e2e = _e2e.chat
init_long_term_memory = _e2e.init_long_term_memory


# 全局长期记忆 (gradio worker 共享)
_LONG_TERM = None


def get_long_term():
    global _LONG_TERM
    if _LONG_TERM is None:
        _LONG_TERM = init_long_term_memory()
    return _LONG_TERM


def chat_fn(message: str, history: list) -> str:
    """Gradio ChatInterface 回调."""
    long_term = get_long_term()
    thread_id = "gradio-default"
    try:
        out = chat_e2e(message, thread_id, long_term)
    except Exception as e:
        return f"❌ 出错: {type(e).__name__}: {e}"

    # 主回复 + 调试信息
    reply = out["reply"]
    debug_lines = [
        f"\n\n---",
        f"*🎯 意图*: `{out['intent']}`",
    ]
    if out["tools_used"]:
        debug_lines.append(f"*🔧 工具*: {out['tools_used']}")
    if out["files"]:
        debug_lines.append(f"*📁 虚拟文件*: {out['files']}")
        # 把 final_report.md 内容也展开
        if "final_report.md" in out.get("files_data", {}):
            debug_lines.append(f"\n**[终稿 final_report.md]**:\n{out['files_data']['final_report.md'][:800]}")

    return reply + "\n".join(debug_lines)


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="hello-my-deep_agents · 端到端 Demo") as demo:
        gr.Markdown(
            """
            # 🚀 hello-my-deep_agents · 端到端研究 Agent

            集大成 demo: **意图识别 + 多层记忆 + RAG + SubAgent + Planning + FS**

            **试试问**:
            - 你好 (闲聊路径)
            - 退货政策是什么? (RAG 路径)
            - 深度研究: LangChain 1.0 vs 0.3 的核心差异 (SubAgent 路径)
            - 钻石会员有什么权益? (RAG 路径)

            **架构**: ChatTongyi (qwen-plus) + LangChain 1.0 + LangGraph 1.1 + DeepAgents 0.5
            """
        )

        gr.ChatInterface(
            fn=chat_fn,
            examples=[
                "你好",
                "退货政策是什么?",
                "深度研究: DeepAgents 比传统 LangChain Agent 强在哪?",
                "qwen-max 和 qwen-long 有什么区别?",
            ],
        )

        gr.Markdown(
            """
            ---
            *Powered by hello-my-deep_agents · 阿里云通义 qwen-plus · DashScope embeddings · Gradio 6*
            """
        )
    return demo


def main() -> None:
    print("=" * 60)
    print("Ch4.3 · 02 全功能 Gradio UI")
    print("=" * 60)
    port = int(os.getenv("GRADIO_PORT", "7861"))
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
