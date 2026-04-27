"""共享搜索工具 — 三个对比脚本都用这个, 保证任务一致.

设计:
    1. 优先用 ddgs (新版 duckduckgo-search) 真搜
    2. 0 结果或异常 → 走 mock 数据 (保证教学场景脚本能跑通)
    3. 真实项目用 Tavily / SerpAPI, 见 Ch4.2.3
"""

from __future__ import annotations

from langchain_core.tools import tool


# 教学用 mock 知识库 — 当 ddgs 不可用时给出"足够 LLM 写报告"的素材
_MOCK_KB: dict[str, str] = {
    "deepagents": """\
DeepAgents 是 LangChain AI 团队 2025 年推出的 Agent 脚手架库, 在 LangGraph 之上封装.
核心特性:
1. Planning Tool (write_todos): LLM 自动列任务清单, 标记 in_progress / completed.
2. Virtual File System: 内置 read_file / write_file / edit_file / ls / glob / grep,
   让 Agent 把中间结果落"虚拟盘", 避免 messages 上下文爆炸.
3. SubAgent: 主 Agent 派生子 Agent 处理隔离任务, 子 Agent 拥有独立 messages.
4. Detailed System Prompt: 内置长指令模板 (~2000 字), 教 LLM 如何用上述工具.
API: create_deep_agent(model, tools, instructions) 三参数即跑.
""",
    "langchain": """\
LangChain 是 LLM 应用开发的通用框架, 提供 LLM / Tool / Memory / Retriever / Chain 抽象.
核心理念: 把 LLM 应用拆成可组合的"乐高积木", 用 LCEL 表达式 (prompt | llm | parser)
拼接. 支持 OpenAI / Anthropic / 通义 / Ollama 等 30+ provider. 是 LLM 时代的 Spring Framework.
""",
    "langgraph": """\
LangGraph 是 LangChain AI 出品的状态机/图编排框架, 在 LangChain 之上.
核心抽象: StateGraph (节点 + 边 + 状态), 用图描述 Agent 工作流.
特性: 断点续跑 (Checkpointer), 流式 (stream_mode), 多 Agent 协调.
是 LLM 时代的 Spring StateMachine.
""",
    "agent": """\
LLM Agent 指能调工具、能多步推理、能自主决策的 LLM 程序. 经典模式:
- ReAct (Reasoning + Acting): 思考-行动-观察循环
- Tool Use / Function Calling: LLM 输出结构化工具调用, 你的代码真实执行
- Planning: 把复杂任务拆成多步, 逐步执行
""",
    "区别": """\
DeepAgents vs 普通 LangChain Agent 的核心区别:
1. 抽象层级: DeepAgents 高层脚手架, 一行启动; 普通 LangChain 需手动拼装
2. Planning: DeepAgents 内置 todo 工具, 普通 Agent 没有
3. 文件系统: DeepAgents 有虚拟 FS 卸载长上下文, 普通 Agent 全部塞 messages
4. SubAgent: DeepAgents 内置子 Agent 派发, 普通 Agent 要自己跑多个 chain
5. 适用场景: DeepAgents 适合长任务(研究/编码), 普通 Agent 适合标准 ReAct
""",
}


def _mock_search(query: str) -> str:
    """根据 query 关键词命中 mock 知识库."""
    query_lower = query.lower()
    matched: list[str] = []
    for key, content in _MOCK_KB.items():
        if key in query_lower or key in query:
            matched.append(content)
    if matched:
        return "\n\n---\n\n".join(matched)
    # 兜底: 返回所有相关内容
    return _MOCK_KB["deepagents"] + "\n\n---\n\n" + _MOCK_KB["区别"]


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """联网搜索关键词, 返回前 N 条摘要.

    Args:
        query: 搜索关键词
        max_results: 最多返回几条 (默认 5)
    """
    # 优先尝试 ddgs (新版 duckduckgo-search)
    try:
        from ddgs import DDGS

        results = list(DDGS().text(query, max_results=max_results))
        if results:
            lines = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "")
                body = (r.get("body") or "")[:200]
                href = r.get("href", "")
                lines.append(f"[{i}] {title}\n{body}\n来源: {href}")
            return "\n\n".join(lines)
    except Exception:
        pass

    # Fallback: mock 知识库 (保证教学场景脚本能跑通)
    return f"[Mock Search] query={query!r}\n\n" + _mock_search(query)


@tool
def write_report(title: str, content: str) -> str:
    """把研究报告写成 markdown (返回完整内容供调用方查看).

    Args:
        title: 报告标题
        content: 报告完整内容 (markdown)
    """
    # 教学场景只返回字符串, 不真实写盘 (避免污染仓库)
    return f"# {title}\n\n{content}"


TOOLS = [web_search, write_report]


RESEARCH_QUESTION = "DeepAgents 和 LangChain 普通 Agent 的核心区别"
