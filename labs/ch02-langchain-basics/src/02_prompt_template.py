"""02 · Prompt 模板 + Few-shot — 把变量塞进提示词.

为什么要用模板:
    硬编码 prompt 字符串 = 没法复用 / 没法 A/B / 没法换语言.
    模板是 LLM 应用的 "Mybatis SQL XML" — 业务和 prompt 分离.

教学要点:
    1. PromptTemplate     — 单字符串模板 (老 API)
    2. ChatPromptTemplate — 多消息模板 (现代主流, system + user + history)
    3. Few-shot — 把示例塞进 prompt 提升 LLM 效果
    4. partial — 模板预填部分变量

Run:
    python 02_prompt_template.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.prompts import (  # noqa: E402
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)


def demo_simple_prompt() -> None:
    """1. 最简模板 — 一个字符串两个变量."""
    print("--- 1. PromptTemplate (单字符串模板) ---")
    template = PromptTemplate.from_template("用一句话介绍 {topic}, 受众是 {audience}.")
    rendered = template.format(topic="DeepAgents", audience="Java 工程师")
    print(f"渲染结果: {rendered}\n")


def demo_chat_prompt() -> None:
    """2. ChatPromptTemplate — 多消息模板, 现代主流."""
    print("--- 2. ChatPromptTemplate (多消息模板, 推荐) ---")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一名{role}, 用{audience}能懂的话回答, 不超过 50 字."),
            ("human", "{question}"),
        ]
    )

    # format_messages 给出真实的消息列表
    messages = prompt.format_messages(
        role="LangChain 资深工程师",
        audience="Java 工程师",
        question="LCEL 比传统 chain 好在哪?",
    )
    print("渲染结果:")
    for m in messages:
        print(f"  [{type(m).__name__}] {m.content[:80]}...")

    # 真实调用 LLM
    llm = get_llm()
    response = llm.invoke(messages)
    print(f"LLM 回复: {response.content}\n")


def demo_partial() -> None:
    """3. partial — 模板预填部分变量, 类似函数偏函数 functools.partial."""
    print("--- 3. partial (预填变量, 复用模板) ---")
    base = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一名 {role}, 用 {audience} 能懂的话回答."),
            ("human", "{question}"),
        ]
    )

    # 预填角色 — 后续只需要传 question
    java_dev_prompt = base.partial(role="LangChain 工程师", audience="Java 工程师")

    msgs = java_dev_prompt.format_messages(question="什么是 prompt 工程?")
    print(f"system: {msgs[0].content}")
    print(f"human:  {msgs[1].content}\n")


def demo_few_shot() -> None:
    """4. Few-shot — 把示例塞进 prompt, 让 LLM 学着模仿."""
    print("--- 4. Few-shot (示例驱动) ---")

    # 准备示例集
    examples = [
        {"input": "苹果", "output": "水果, 红色或绿色, 圆形"},
        {"input": "汽车", "output": "交通工具, 4 个轮子, 钢铁制"},
        {"input": "Python", "output": "编程语言, 解释执行, 缩进语法"},
    ]

    example_prompt = ChatPromptTemplate.from_messages(
        [("human", "{input}"), ("ai", "{output}")]
    )

    few_shot = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "请按照示例的风格回答 — 简短的描述."),
            few_shot,
            ("human", "{input}"),
        ]
    )

    # 看看渲染出来的完整消息
    msgs = final_prompt.format_messages(input="LangGraph")
    print(f"完整消息列表 ({len(msgs)} 条):")
    for m in msgs:
        prefix = type(m).__name__.replace("Message", "").lower()
        print(f"  [{prefix:>6}] {m.content[:60]}...")

    # 真实调用
    llm = get_llm()
    response = llm.invoke(msgs)
    print(f"LLM 回复: {response.content}")


def main() -> None:
    print("=" * 60)
    print("Ch2 · 02 Prompt 模板 + Few-shot")
    print("=" * 60)

    demo_simple_prompt()
    demo_chat_prompt()
    demo_partial()
    demo_few_shot()


if __name__ == "__main__":
    main()
