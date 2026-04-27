"""环境健康检查 — 跑任何 lab 之前先 python scripts/check-env.py.

检查项:
  1. Python 版本 >= 3.10
  2. .env 是否存在且 DASHSCOPE_API_KEY 不是占位符
  3. 关键依赖是否安装
  4. (可选) docker 中间件是否可达
  5. LLM 实际调用是否通
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def ok(msg: str) -> None:
    print(f"{GREEN}✅{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}⚠️ {RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}❌{RESET} {msg}")


def check_python() -> bool:
    if sys.version_info < (3, 10):
        fail(f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.10")
        return False
    ok(f"Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_env_file() -> bool:
    env = REPO_ROOT / ".env"
    if not env.exists():
        fail(".env 不存在. 执行: cp .env.example .env, 然后填上你的 key")
        return False
    ok(".env 文件存在")

    from dotenv import load_dotenv

    load_dotenv(env)

    key = os.getenv("DASHSCOPE_API_KEY", "")
    if not key or key.startswith("sk-xxx"):
        fail("DASHSCOPE_API_KEY 未设置或是占位符")
        return False
    ok(f"DASHSCOPE_API_KEY 已配置 (前缀 sk-{key[3:8]}...)")
    return True


def check_deps() -> bool:
    """检查必需依赖. 可选依赖 (gradio/pgvector/redis) 单独检查."""
    required = [
        "langchain",
        "langchain_core",
        "langchain_community",
        "langgraph",
        "dashscope",
        "dotenv",
    ]
    optional = {
        "deepagents": "Ch4 实战篇所有 lab 都用",
        "fastapi": "Ch1.07 / Ch4 实战篇 Web 接入",
        "gradio": "Ch4.1 / Ch4.3 网页对话 UI",
        "ddgs": "Ch3 / Ch4 联网搜索 (备选 tavily)",
    }

    # 必需依赖
    missing_required = []
    for d in required:
        try:
            importlib.import_module(d)
        except ImportError:
            missing_required.append(d)

    if missing_required:
        fail(f"缺失必需依赖: {missing_required}. 执行: pip install -r requirements.txt")
        return False
    ok(f"必需依赖已安装 ({len(required)} 个)")

    # 可选依赖 — 缺也不算失败, 但提示
    missing_optional = []
    for d, desc in optional.items():
        try:
            importlib.import_module(d)
        except ImportError:
            missing_optional.append((d, desc))

    if missing_optional:
        for d, desc in missing_optional:
            warn(f"可选依赖 {d} 未装 — {desc}")
    else:
        ok(f"可选依赖已安装 ({len(optional)} 个)")

    return True


def check_llm_call() -> bool:
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from common.llm import get_llm

        llm = get_llm()
        resp = llm.invoke("用一个字回答: 1+1=?")
        content = (resp.content if hasattr(resp, "content") else str(resp))[:30]
        ok(f"LLM 调用成功: {content!r}")
        return True
    except Exception as e:
        fail(f"LLM 调用失败: {e}")
        return False


def check_optional_middleware() -> None:
    """可选中间件 — 不影响 Ch1/Ch2/Ch3/Ch4.1/Ch4.2.4 等 lab 跑通."""
    print()
    print("--- 可选中间件 (仅 Memory / RAG lab 需要) ---")

    try:
        import socket

        host = os.getenv("PGVECTOR_HOST", "localhost")
        port = int(os.getenv("PGVECTOR_PORT", "5432"))
        with socket.create_connection((host, port), timeout=2):
            ok(f"PgVector @ {host}:{port}")
    except Exception:
        warn("PgVector 不可达 (Memory/RAG lab 需要; docker compose up -d pgvector)")

    try:
        import socket

        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        with socket.create_connection((host, port), timeout=2):
            ok(f"Redis    @ {host}:{port}")
    except Exception:
        warn("Redis 不可达 (Memory lab 需要; docker compose up -d redis)")


def main() -> int:
    print("=" * 60)
    print("hello-my-deep_agents 环境健康检查")
    print("=" * 60)

    results = [
        check_python(),
        check_env_file(),
        check_deps(),
        check_llm_call(),
    ]
    check_optional_middleware()

    print()
    print("=" * 60)
    if all(results):
        print(f"{GREEN}全部必检项通过 — 可以开始跑 lab 了{RESET}")
        return 0
    print(f"{RED}有必检项失败 — 请按上面的提示修复后再跑 lab{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
