"""03 · LCEL 链式表达式 — LangChain 的"管道操作".

LCEL = LangChain Expression Language

核心抽象: Runnable 接口
    每个组件 (prompt, llm, parser) 都实现 Runnable.
    用 | 操作符把它们串起来 — 类似 Unix pipe / Java Stream.

教学要点:
    1. 基础 chain: prompt | llm | parser
    2. 结构化输出: with_structured_output(Schema)
    3. RunnableLambda: 把普通函数嵌进 chain
    4. RunnableParallel: 并行分支

Run:
    python 03_lcel_chain.py
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
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnableLambda, RunnableParallel  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


def demo_basic_chain() -> None:
    """1. 基础 LCEL: prompt | llm | parser."""
    print("--- 1. 基础链 prompt | llm | parser ---")
    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")
    llm = get_llm()
    parser = StrOutputParser()  # 把 AIMessage 提取成纯字符串

    chain = prompt | llm | parser  # 这一行就是 LCEL 的精髓

    result = chain.invoke({"topic": "DeepAgents"})
    print(f"结果 (str): {result}\n")


def demo_structured_output() -> None:
    """2. 结构化输出 — 让 LLM 返回 Pydantic 对象."""
    print("--- 2. 结构化输出 with_structured_output ---")

    class FrameworkInfo(BaseModel):
        """一个开源框架的结构化信息."""

        name: str = Field(description="框架名称")
        language: str = Field(description="主要编程语言")
        first_release_year: int = Field(description="首次发布年份")
        github_stars: int | None = Field(default=None, description="GitHub stars (估)")
        use_cases: list[str] = Field(description="3 个典型应用场景")

    prompt = ChatPromptTemplate.from_template("提供 {framework} 的结构化信息")
    llm = get_llm()
    structured_llm = llm.with_structured_output(FrameworkInfo)

    chain = prompt | structured_llm
    result: FrameworkInfo = chain.invoke({"framework": "LangChain"})

    print(f"name           : {result.name}")
    print(f"language       : {result.language}")
    print(f"first_release  : {result.first_release_year}")
    print(f"github_stars   : {result.github_stars}")
    print(f"use_cases      : {result.use_cases}")
    print()


def demo_runnable_lambda() -> None:
    """3. RunnableLambda — 把普通 Python 函数嵌进 chain."""
    print("--- 3. RunnableLambda (普通函数嵌入) ---")

    def to_upper(text: str) -> str:
        return text.upper()

    def add_emoji(text: str) -> str:
        return f"🚀 {text} 🎯"

    prompt = ChatPromptTemplate.from_template("一句话回答: {q}")
    llm = get_llm()
    parser = StrOutputParser()

    # 最后两步是普通 Python 函数, 用 RunnableLambda 包一下嵌进 chain
    chain = (
        prompt
        | llm
        | parser
        | RunnableLambda(to_upper)
        | RunnableLambda(add_emoji)
    )

    # 注意: emoji 在 GBK 终端可能乱码, PYTHONIOENCODING=utf-8 防御
    result = chain.invoke({"q": "用一个英文单词描述 langchain"})
    print(f"结果 (经过 to_upper + add_emoji): {result!r}\n")


def demo_runnable_parallel() -> None:
    """4. RunnableParallel — 并行多个 chain, 结果合并成 dict."""
    print("--- 4. RunnableParallel (并行分支) ---")
    llm = get_llm()
    parser = StrOutputParser()

    # 三个独立 chain, 用同一个输入, 并行跑
    pros_chain = (
        ChatPromptTemplate.from_template("一句话: {topic} 的优点是?")
        | llm
        | parser
    )
    cons_chain = (
        ChatPromptTemplate.from_template("一句话: {topic} 的缺点是?")
        | llm
        | parser
    )
    summary_chain = (
        ChatPromptTemplate.from_template("一句话: {topic} 一句话总结")
        | llm
        | parser
    )

    parallel = RunnableParallel(
        pros=pros_chain,
        cons=cons_chain,
        summary=summary_chain,
    )

    result = parallel.invoke({"topic": "LangChain"})
    print(f"pros    : {result['pros']}")
    print(f"cons    : {result['cons']}")
    print(f"summary : {result['summary']}")


def main() -> None:
    print("=" * 60)
    print("Ch2 · 03 LCEL 链式表达式")
    print("=" * 60)

    demo_basic_chain()
    demo_structured_output()
    demo_runnable_lambda()
    demo_runnable_parallel()

    print("\n--- 关键点 ---")
    print("  - LCEL 的 | 操作符把任意 Runnable 串起来")
    print("  - with_structured_output(Schema) 让 LLM 直接返回 Pydantic 对象")
    print("  - RunnableLambda / RunnableParallel 让普通函数和并行分支无缝嵌入")
    print("  - chain.invoke / .stream / .ainvoke 都自动支持, 不用改代码")


if __name__ == "__main__":
    main()
