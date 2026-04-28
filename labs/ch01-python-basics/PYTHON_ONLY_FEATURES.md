# Python 独有特性专章 · Java 工程师必读

> 看完 [PYTHON_VS_JAVA.md](PYTHON_VS_JAVA.md) 你会觉得 Python 和 Java 差不多. 错. **本章是 Python 在 Java 永远学不会的地方** —— 这些不是语法糖, 是 Python 之所以为 Python 的灵魂.

读完本章你会明白: 为什么 LangChain / FastAPI / Pydantic / PyTorch 全部选 Python 而不是 Java —— 这些框架的优雅都建立在下面这些机制上.

---

## 总览速查

| 特性 | 一句话本质 | 等价 Java? | 教程哪些 lab 用 |
|---|---|---|---|
| Duck Typing | 看着像鸭子就当鸭子用, 不查类型 | 无, 只能 interface + impl | 全教程, LangChain Runnable |
| Decorator | 函数装饰函数, 一行注入横切逻辑 | 注解 + 注解处理器 (远不如灵活) | Ch1, Ch3 工具注册, Ch7 Reflection |
| Generator (yield) | 惰性产生序列, 用一个产一个 | 无, 只能 Iterator + 状态机 | Ch4 流式 RAG, Ch6 stream pattern |
| Context Manager (with) | 进入/退出自动执行, 资源安全 | try-with-resources (弱化版) | Ch2 LLM client, Ch3 file io |
| List/Dict/Set Comprehension | 一行生成集合 | Stream API (语法笨重) | 全教程, prompt 模板生成 |
| `*args **kwargs` | 收集任意位置/关键字参数 | 可变参数 + Map (没法链式传) | Ch3 工具 schema |
| Multiple Return + Tuple Unpacking | 直接返回多值并解构 | 必须 record / Pair / Triple | Ch4 retriever 返回 (docs, scores) |
| 多重继承 + MRO | 一个类继承多个父类 | 不允许, 只能 interface | Ch6 mixin agent traits |
| Metaclass | 类是对象, 可被另一个类制造 | 无, 反射也做不到 | Ch3 Pydantic 内部 |
| GIL | 同一时刻只有一个线程跑 Python 字节码 | 无, JVM 真多线程 | Ch6 async 必备认知 |
| `__slots__` | 限定实例属性, 节省内存 | 无, Java 字段已经是 slot | Ch5 大量小对象优化 |
| Protocol (structural typing) | 鸭子类型的静态版本 | 无, Java 名义类型 | Ch3 工具签名约定 |
| `__enter__/__exit__` | 让你的类支持 with | AutoCloseable (弱化版) | Ch3 自定义 retriever |
| `__iter__/__next__` | 让你的类支持 for 循环 | Iterable (Java 等价但更繁琐) | Ch4 自定义召回器 |
| f-string 高级格式化 | 嵌入变量/表达式/格式说明 | `String.formatted` (功能弱) | 全教程 |

---

## 1. Duck Typing — 看着像鸭子就当鸭子

**本质**: Python 调用 `obj.method()` 时, 不检查 obj 是不是某个 interface 的实例 — 只检查它有没有这个方法. 有就跑, 没有就 AttributeError.

```python
class Duck:
    def quack(self): print("嘎嘎")

class Person:
    def quack(self): print("我假装是鸭子")

def make_it_quack(thing):
    thing.quack()  # 不管 thing 是什么类型, 有 quack() 就行

make_it_quack(Duck())     # 嘎嘎
make_it_quack(Person())   # 我假装是鸭子
```

**Java 等价**: 必须先定义 `interface Quackable { void quack(); }`, 然后 `class Duck implements Quackable`. Java 是 *名义类型* (类型靠名字声明), Python 是 *结构类型* (类型靠形状).

**为什么重要**: LangChain 的 `Runnable` 协议就是 duck typing — 任何有 `invoke()` 方法的对象都能塞进 chain. 你不用 implements 任何东西.

---

## 2. Decorator — 一行注入横切逻辑

**本质**: 装饰器是 *接受函数返回函数* 的高阶函数. 通过 `@xxx` 语法在定义时包裹原函数.

```python
def timing(func):
    def wrapper(*args, **kwargs):
        import time; t0 = time.time()
        r = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time()-t0:.3f}s")
        return r
    return wrapper

@timing
def slow_query():
    import time; time.sleep(1)
    return "done"

slow_query()  # 自动打印耗时
```

**Java 等价**: 注解 (`@Override`) 是 *元数据*, 不能改变行为. 想做装饰器只能用 Spring AOP / AspectJ — 需要 IoC 容器 + 反射.

**为什么重要**: FastAPI 的 `@app.get("/")` / Pydantic 的 `@validator` / pytest 的 `@pytest.fixture` 全是装饰器. 没有装饰器, Python 生态会塌一半.

---

## 3. Generator (yield) — 惰性产序列

**本质**: 用 `yield` 替代 `return`, 函数变成一个可迭代对象 — 调一次产一个, 不调不产, 不占内存.

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a            # 暂停, 给调用方一个值
        a, b = b, a + b

for x in fib(10):
    print(x)               # 0 1 1 2 3 5 8 13 21 34

# 生成器表达式 — 不立即计算, 占常量内存
squares = (x*x for x in range(1_000_000))
```

**Java 等价**: 没有. Java 8 的 Stream 是惰性求值但只能链式. 想要 yield 风格只能 Reactor Flux + 手动状态机.

**为什么重要**: LLM 流式输出 (token by token) 在 Python 是 `async def stream(): yield token`, 在 Java 是 `Flux<String>`. RAG 检索 100 万文档时, generator 让你只在用到时才加载.

---

## 4. Context Manager (with) — 进入/退出自动执行

**本质**: 任何实现 `__enter__` 和 `__exit__` 的对象都能用 with 语句, 进入时调 enter, 退出时无论是否抛异常都调 exit.

```python
with open("data.txt") as f:        # f.__enter__() 打开
    text = f.read()                # 用
# f.__exit__() 自动关闭, 哪怕中间抛异常也保证关

# 自定义
class Timer:
    def __enter__(self): import time; self.t0 = time.time(); return self
    def __exit__(self, *exc): import time; print(f"{time.time()-self.t0:.3f}s")

with Timer():
    do_expensive_work()            # 自动计时
```

**Java 等价**: try-with-resources 仅限 AutoCloseable 接口, 只能 close, 不能写自定义 enter/exit.

**为什么重要**: LangChain 的 callback handler / Pydantic 的 model context / SQLAlchemy 的 session 全用 with.

---

## 5. Comprehension (List/Dict/Set) — 一行生成集合

**本质**: `[expr for x in iter if cond]` 是 *声明式集合构造* — 像 SQL 一样描述要什么, 而不是怎么做.

```python
# 列表推导
squares = [x*x for x in range(10) if x % 2 == 0]   # [0, 4, 16, 36, 64]

# 字典推导
name_to_len = {n: len(n) for n in ["alice", "bob"]}

# 集合推导
unique_lens = {len(n) for n in ["alice", "bob", "eve"]}

# 嵌套
matrix = [[i*j for j in range(3)] for i in range(3)]
```

**Java 等价**: Stream API `list.stream().filter(...).map(...).toList()` 功能等价但语法繁重 — 5 行能换 1 行.

**为什么重要**: Pythonic 代码的 *视觉密度*. LLM prompt 模板填充经常 `[fmt.format(x=x) for x in items]` 一行搞定; Java 同样事情要 5 行 stream chain.

---

## 6. `*args` 和 `**kwargs` — 收集任意参数

**本质**: `*args` 把多余位置参数装成 tuple, `**kwargs` 把多余 key=value 装成 dict. 反过来 `f(*args, **kwargs)` 把它们解包传出去.

```python
def log(*args, **kwargs):
    print("positional:", args)        # tuple
    print("keyword:   ", kwargs)      # dict

log("a", "b", user="alice", role="admin")
# positional: ('a', 'b')
# keyword:    {'user': 'alice', 'role': 'admin'}

# 转发参数 — 装饰器/包装器神器
def wrap(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)  # 透传一切
    return inner
```

**Java 等价**: `Object... args` 仅支持位置, 关键字参数得自己用 `Map<String,Object>`, 调用方必须自己 `Map.of(...)`, 没法链式透传.

**为什么重要**: LangChain 工具签名 `def tool(query: str, **kwargs)` 让 LLM 任意填参数, 工具自己接住. Java 同样事情要写 `Map<String, Object>` + 类型校验.

---

## 7. Multiple Return + Tuple Unpacking — 直接返回多值

**本质**: Python 函数可以返回 tuple, 调用方可以解构.

```python
def divmod_pair(a, b):
    return a // b, a % b           # 实际返回 tuple

q, r = divmod_pair(17, 5)          # 解构: q=3, r=2

# 多变量交换 — Pythonic 神操作
a, b = b, a                        # 不需要 tmp 变量

# 嵌套解构
((x, y), z) = ((1, 2), 3)

# * 收集剩余
first, *rest = [1, 2, 3, 4]        # first=1, rest=[2,3,4]
```

**Java 等价**: JDK 14+ 的 record 是替代品, 但要先定义 record 类型. Python 不需要任何声明.

**为什么重要**: RAG 检索器 `docs, scores = retriever.search(q)` 一行解构. Java 必须 `SearchResult result = retriever.search(q); var docs = result.docs(); var scores = result.scores();`.

---

## 8. 多重继承 + MRO (Method Resolution Order)

**本质**: Python 类可以继承多个父类, 用 C3 算法决定方法查找顺序.

```python
class A:
    def hi(self): print("A")
class B:
    def hi(self): print("B")
class C(A, B):                     # 多重继承
    pass

C().hi()                           # 'A' (先找 A 后 B)
print(C.__mro__)                   # (C, A, B, object)
```

**Java 等价**: 不允许类多重继承, 只能 implements 多 interface. interface 默认方法 (Java 8+) 提供有限的 mixin 能力, 但不支持状态.

**为什么重要**: Python 的 mixin 模式靠多重继承, 让一个类同时拥有 `Loggable / Cacheable / Validatable` 多种能力. LangChain 内部大量用.

---

## 9. Metaclass — 类的类

**本质**: Python 中 *类也是对象*, 类的类型叫 metaclass (默认是 `type`). 自定义 metaclass 可以在类定义时介入, 修改类本身.

```python
class AutoLog(type):
    def __new__(mcs, name, bases, attrs):
        # 类被创建前介入, 修改 attrs (例如自动加日志)
        for k in list(attrs.keys()):
            v = attrs[k]
            if callable(v) and not k.startswith("_"):
                attrs[k] = lambda *a, _v=v, **kw: (print(f"call {_v.__name__}"), _v(*a, **kw))[1]
        return super().__new__(mcs, name, bases, attrs)

class MyService(metaclass=AutoLog):
    def foo(self): return 1

MyService().foo()                  # 自动打 'call foo'
```

**Java 等价**: 没有. 反射 (Reflection) 只能读不能改类定义; 字节码工程 (ASM/Byte Buddy) 能做但脱离语法层.

**为什么重要**: Pydantic 的 `BaseModel` 用 metaclass 在类定义时收集字段并生成 validator. Django ORM 的 Model 同理. 你不会直接写 metaclass, 但理解它能让你看懂 Pydantic 源码.

---

## 10. GIL (Global Interpreter Lock)

**本质**: CPython 实现里有全局锁, 同一时刻只有一个线程跑 Python 字节码. 多线程在 *CPU 密集任务* 上不能加速, 但在 *I/O 密集任务* 上有效 (I/O 时释放 GIL).

```python
# CPU 密集 — GIL 让多线程没用, 必须用 multiprocessing 真并行
from multiprocessing import Pool
with Pool(4) as p: p.map(heavy_compute, items)

# I/O 密集 — 多线程或 asyncio 都行 (I/O 期间 GIL 释放)
import asyncio
await asyncio.gather(*[fetch(url) for url in urls])
```

**Java 等价**: 没有. JVM 真正多线程, 多核 CPU 满血跑.

**为什么重要**: LLM 调用是 I/O 密集 (等网络), 用 asyncio 完美; 模型推理是 CPU/GPU 密集, 必须 multiprocessing 或外置服务. 不懂 GIL 写出来的 Python 程序看似多线程实则单核.

> 注: Python 3.13 引入 free-threaded build (PEP 703) 实验性移除 GIL, 但生产稳定 5+ 年内还得当 GIL 存在.

---

