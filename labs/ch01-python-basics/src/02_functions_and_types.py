"""02 · 函数与类型提示 — 把 Java 方法签名翻译成 Python.

对照表:
    Java                            Python
    ──────                          ──────
    public String foo(int x)         def foo(x: int) -> str
    public List<String> bar()        def bar() -> list[str]
    public Optional<User> find(id)   def find(id: str) -> User | None
    public void baz(int... args)     def baz(*args: int) -> None
    public void qux(Map<K,V> kv)     def qux(**kv: int) -> None
    method overloading 重载           不支持, 用默认参数 / @overload 模拟

Run:
    python 02_functions_and_types.py
"""

from __future__ import annotations


# ===== 1. 基础函数 =====
def add(x: int, y: int) -> int:
    """两数相加 — type hints 可选, 但强烈推荐写."""
    return x + y


# ===== 2. 默认参数 (Java 没有, 必须重载方法) =====
def greet(name: str, greeting: str = "Hello") -> str:
    """默认参数让"重载"变成一行代码."""
    return f"{greeting}, {name}!"


# ===== 3. 可变参数 (Java 的 String...) =====
def sum_all(*numbers: int) -> int:
    """*numbers 收集任意个位置参数为 tuple."""
    return sum(numbers)


# ===== 4. 关键字参数 (Java 没有直接对应, 类似 Map<String, Object>) =====
def build_user(**attrs: str) -> dict[str, str]:
    """**attrs 收集任意个 key=value 为 dict."""
    return attrs


# ===== 5. 多返回值 — Python 用 tuple, Java 要自己 wrap 一个类 =====
def divmod_pair(a: int, b: int) -> tuple[int, int]:
    """同时返回商和余数 — 调用方可解构."""
    return a // b, a % b


# ===== 6. 可空类型 — Python 3.10+ 用 X | None =====
def find_user(user_id: str) -> dict[str, str] | None:
    """模拟一个可能找不到用户的查询 — 对照 Java 的 Optional<User>."""
    if user_id == "alice":
        return {"id": "alice", "role": "admin"}
    return None


# ===== 7. 高阶函数 — 函数当参数, Java 要 Functional Interface =====
def apply(func, value):
    """对照 Java 8 lambda: Function<T, R>.apply(t)."""
    return func(value)


# ===== 8. lambda — 一行匿名函数 =====
square = lambda x: x * x  # noqa: E731


# ===== 9. 闭包 — 函数捕获外部变量 =====
def make_counter(start: int = 0):
    """闭包: 内层函数捕获外层 count, 每次调用 += 1."""
    count = start

    def inc() -> int:
        nonlocal count  # 修改外层变量必须用 nonlocal
        count += 1
        return count

    return inc


def main() -> None:
    print(f"add(2, 3)             = {add(2, 3)}")
    print(f"greet('Alice')        = {greet('Alice')}")
    print(f"greet('Bob', '你好')  = {greet('Bob', '你好')}")
    print(f"sum_all(1,2,3,4,5)    = {sum_all(1, 2, 3, 4, 5)}")
    print(f"build_user(...)       = {build_user(name='alice', role='admin')}")
    print(f"divmod_pair(17, 5)    = {divmod_pair(17, 5)}")
    print(f"find_user('alice')    = {find_user('alice')}")
    print(f"find_user('zzz')      = {find_user('zzz')}")
    print(f"apply(square, 7)      = {apply(square, 7)}")

    counter = make_counter(10)
    print(f"counter() x3          = {counter()}, {counter()}, {counter()}")


if __name__ == "__main__":
    main()
