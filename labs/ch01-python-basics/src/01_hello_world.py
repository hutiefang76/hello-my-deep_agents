"""01 · Hello World — Python 程序的入口长什么样.

对照 Java: public static void main(String[] args) { ... }
对照 Python: 没有"main 方法", 而是用 if __name__ == "__main__": 守护

Why:
    Python 文件天然就是脚本, import 时会从上到下执行. 用 __name__ 守护可以
    区分 "被执行" 和 "被 import" 两种场景 — 这是 Python 第一个反直觉点.

Run:
    python 01_hello_world.py
"""

# Python 3 默认 UTF-8, 不像 Java 还需要 -Dfile.encoding=UTF-8
print("Hello, hello-my-deep_agents! 你好, 深度智能体!")


def greet(name: str) -> str:
    """打招呼函数 — type hint 是可选的, 但写了 IDE 和后续 LLM 类库都更友好."""
    return f"Hello, {name}!"


def main() -> None:
    """惯用入口函数 — 让 import 此模块的人能复用 main 逻辑."""
    print(greet("DeepAgents"))
    print(greet("Java 工程师"))

    # 演示: 当此文件被 import 时, 下面的代码不会执行
    print(f"__name__ = {__name__}")
    print(f"__file__ = {__file__}")


if __name__ == "__main__":
    # 这个守护是 Python 第一个反直觉概念:
    # - 直接 python 01_hello_world.py 运行时, __name__ == "__main__", 进入此分支
    # - 被 from xxx import 01_hello_world 时, __name__ == "01_hello_world", 跳过此分支
    main()
