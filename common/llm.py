"""LLM 工厂 — 所有 lab 通过这里拿 LLM 实例.

支持三种 provider, 通过 .env 中 LLM_PROVIDER 切换:
  - tongyi (默认):     阿里云通义 DashScope, 用 ChatTongyi
  - openai_compat:     OpenAI 兼容协议, 走 ChatOpenAI + base_url
  - ollama:            本地 Ollama, 走 ChatOllama

为什么这样设计:
  1. 学员只配一次 .env, 全部 lab 直接跑
  2. 切换模型 = 改一行 .env, 不动代码
  3. 教学时可以演示"同一段代码切不同 LLM"
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _load_env_once() -> None:
    """从仓库根目录的 .env 加载环境变量.

    向上找最多 5 层目录, 找到 .env 即停 — 这样无论 lab 嵌套多深都能找到.
    """
    cur = Path(__file__).resolve().parent
    for _ in range(5):
        env_file = cur / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=False)
            return
        cur = cur.parent
    load_dotenv(override=False)


_load_env_once()


@lru_cache(maxsize=8)
def get_llm(
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    streaming: bool = False,
):
    """返回一个 LangChain BaseChatModel 实例.

    优先级: 函数参数 > 环境变量 > 默认值.

    Examples:
        >>> llm = get_llm()                       # 用 .env 默认 (tongyi + qwen-plus)
        >>> llm = get_llm(model="qwen-max")       # 切大模型
        >>> llm = get_llm(provider="ollama")      # 切本地
    """
    provider = (provider or os.getenv("LLM_PROVIDER", "tongyi")).lower()
    model = model or os.getenv("LLM_MODEL", "qwen-plus")
    if temperature is None:
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    if provider == "tongyi":
        return _build_tongyi(model, temperature, streaming)
    if provider in ("openai_compat", "openai"):
        return _build_openai_compat(model, temperature, streaming)
    if provider == "ollama":
        return _build_ollama(model, temperature, streaming)
    raise ValueError(
        f"未知 LLM_PROVIDER='{provider}', 应为 tongyi / openai_compat / ollama"
    )


def _build_tongyi(model: str, temperature: float, streaming: bool):
    from langchain_community.chat_models import ChatTongyi

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key or api_key.startswith("sk-xxx"):
        raise RuntimeError(
            "DASHSCOPE_API_KEY 未设置或仍是占位符. "
            "请到 https://bailian.console.aliyun.com/?apiKey=1 申请, "
            "然后填入 .env"
        )
    return ChatTongyi(
        model=model,
        api_key=api_key,
        temperature=temperature,
        streaming=streaming,
    )


def _build_openai_compat(model: str, temperature: float, streaming: bool):
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv(
        "OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY (或 DASHSCOPE_API_KEY) 未设置. 请检查 .env"
        )
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        streaming=streaming,
    )


def _build_ollama(model: str, temperature: float, streaming: bool):
    try:
        from langchain_ollama import ChatOllama
    except ImportError as e:
        raise RuntimeError(
            "langchain-ollama 未安装. pip install langchain-ollama"
        ) from e

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
    )


@lru_cache(maxsize=4)
def get_embeddings():
    """返回 Embedding 模型实例.

    DashScope 的 text-embedding-v3 维度 1024, 是 RAG lab 的默认选择.
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "tongyi").lower()
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

    if provider == "tongyi":
        from langchain_community.embeddings import DashScopeEmbeddings

        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key or api_key.startswith("sk-xxx"):
            raise RuntimeError("DASHSCOPE_API_KEY 未设置, 无法初始化 embedding")
        return DashScopeEmbeddings(model=model, dashscope_api_key=api_key)

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(
            model=model, base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )

    raise ValueError(f"未知 EMBEDDING_PROVIDER='{provider}'")


if __name__ == "__main__":
    # 自检脚本: python -m common.llm
    print("=== LLM 自检 ===")
    print(f"LLM_PROVIDER = {os.getenv('LLM_PROVIDER', 'tongyi')}")
    print(f"LLM_MODEL    = {os.getenv('LLM_MODEL', 'qwen-plus')}")
    try:
        llm = get_llm()
        print(f"LLM 实例 OK: {type(llm).__name__}")
        resp = llm.invoke("说一句话: 你好")
        print(f"调用结果 OK: {resp.content[:50]}...")
    except Exception as e:
        print(f"❌ 失败: {e}")
        raise
