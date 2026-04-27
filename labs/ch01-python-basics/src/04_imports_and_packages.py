"""04 · 模块、包与 import — Python 的 package system.

对照:
    Java                                     Python
    ──────                                   ──────
    package com.foo.bar;                     文件放在 foo/bar/ 目录, 加 __init__.py
    import com.foo.bar.Baz;                  from foo.bar import Baz
    import com.foo.bar.*;                    from foo.bar import *  (不推荐)
    import static com.foo.Bar.METHOD;        from foo.bar import METHOD (函数本身)
    classpath                                sys.path

关键概念:
    - 一个 .py 文件 = 一个 module
    - 一个含 __init__.py 的目录 = 一个 package
    - import 是按 sys.path 顺序找的, 不是 Java 的 classpath

Run:
    python 04_imports_and_packages.py

注意: 这个脚本演示了"一个文件内"能玩的 import 形式. 真正的多文件 package
      演示在 _demo_package/ 子目录里, 文末会调用一下.
"""

from __future__ import annotations

# ===== 1. 标准库 import =====
import os
import sys
from pathlib import Path

# ===== 2. 同包内的 import — 演示用 _demo_package =====
# 这里使用绝对路径让 import 能工作 (sys.path 调整)
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

# noqa 让 lint 工具知道这个 import 是有意放后面的
from _demo_package import math_utils  # noqa: E402
from _demo_package.string_utils import reverse, snake_to_camel  # noqa: E402


def show_paths() -> None:
    """展示 Python 找模块的搜索路径 (相当于 Java 的 -cp / -classpath)."""
    print("--- sys.path (Python 找模块的顺序) ---")
    for i, p in enumerate(sys.path[:5], 1):
        print(f"  [{i}] {p}")
    print(f"  ... 共 {len(sys.path)} 项")


def show_module_info() -> None:
    """展示模块的元信息 — 每个 module 都有这些."""
    print("\n--- 当前模块元信息 ---")
    print(f"  __name__ = {__name__}")
    print(f"  __file__ = {__file__}")
    print(f"  os.__file__ = {os.__file__}")  # 标准库 os 模块的位置


def call_demo_package() -> None:
    """调用同包内的子模块 — 演示 import 链路工作."""
    print("\n--- 调用 _demo_package ---")
    print(f"math_utils.add(3, 4)         = {math_utils.add(3, 4)}")
    print(f"math_utils.PI                = {math_utils.PI}")
    print(f"reverse('hello')             = {reverse('hello')}")
    print(f"snake_to_camel('user_name')  = {snake_to_camel('user_name')}")


def main() -> None:
    show_paths()
    show_module_info()
    call_demo_package()

    print("\n--- 关键点 ---")
    print("1. 一个 .py = 一个 module")
    print("2. 一个含 __init__.py 的目录 = 一个 package")
    print("3. import 按 sys.path 顺序找, 第一个匹配的赢")
    print("4. from X import Y 把 Y 直接放进当前命名空间 (Java 的 import static)")
    print("5. import X 把整个 module 引进来, 用 X.Y 访问 (Java 的 import)")


if __name__ == "__main__":
    main()
