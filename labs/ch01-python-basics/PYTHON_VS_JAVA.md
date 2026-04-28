# Python vs Java · 三列对照圣经

> 给 Java 老兵的翻译表。**先建心智模型，再读代码**——本表覆盖 30+ 高频写法，含 Java 8 老写法 / JDK 23 新写法 / Python 写法的横向对照。

每一行末尾的 📁 ref 链接到具体的 .py 行号，方便跳转看源码。

---

## 入口与脚本

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `public static void main(String[] args)` | 同左 (instance main JEP 463 仍是预览) | `if __name__ == "__main__":` | 📁 [01_hello_world.py:33](src/01_hello_world.py#L33) |
| `System.out.println("Hello %s".formatted(x))` | text block 加 .formatted(x) | `print(f"Hello {x}")` | 📁 [01_hello_world.py:15](src/01_hello_world.py#L15) |
| `String s = "hi";` | `var s = "hi";` (JDK 10+) | `s = "hi"` | 📁 [02_functions_and_types.py:21](src/02_functions_and_types.py#L21) |
## 函数与类型

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `public String foo(int x)` | 同左 (语法不变) | `def foo(x: int) -> str:` | 📁 [02_functions_and_types.py:21](src/02_functions_and_types.py#L21) |
| `Optional<User> find(id)` | 同左 + pattern matching | `def find(id) -> User \| None:` | 📁 [02_functions_and_types.py:51](src/02_functions_and_types.py#L51) |
| `void baz(int... args)` | 同左 | `def baz(*args: int):` | 📁 [02_functions_and_types.py:33](src/02_functions_and_types.py#L33) |
| 多返回值要新建 POJO | `record DivMod(int q, int r)` | `return a // b, a % b` (tuple) | 📁 [02_functions_and_types.py:45](src/02_functions_and_types.py#L45) |
| 方法重载 (overload) | 同左 | 不支持，用默认参数 / `@overload` 模拟 | 📁 [02_functions_and_types.py:27](src/02_functions_and_types.py#L27) |
| `Function<T,R>.apply(t)` | Stream API + lambda | `func(value)` (函数即对象) | 📁 [02_functions_and_types.py:59](src/02_functions_and_types.py#L59) |

## 类与 OOP

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `public class User` + 手写 ctor/getter/setter/equals/hashCode | `record User(String id, int age)` | `@dataclass class User: id: str; age: int` | 📁 [03_classes_and_oop.py:67](src/03_classes_and_oop.py#L67) |
| `@Data` (Lombok) | `record` (内置, 无需注解处理器) | `@dataclass` (内置) | 📁 [03_classes_and_oop.py:67](src/03_classes_and_oop.py#L67) |
| `extends Animal` | 同左 | `class Dog(Animal):` | 📁 [03_classes_and_oop.py:54](src/03_classes_and_oop.py#L54) |
| `@Override` | 同左 (建议加) | 不需要 (直接定义同名方法) | 📁 [03_classes_and_oop.py:61](src/03_classes_and_oop.py#L61) |
| `abstract class Shape` | `sealed interface Shape permits Circle, Rectangle` | `class Shape(ABC): @abstractmethod def area(self):` | 📁 [03_classes_and_oop.py:102](src/03_classes_and_oop.py#L102) |
| `if (x instanceof Circle) { Circle c = (Circle) x; ... }` | `case Circle c -> ...` (pattern matching) | `if isinstance(x, Circle):` (但 Pythonic 用 duck typing) | 📁 [03_classes_and_oop.py:158](src/03_classes_and_oop.py#L158) |
| `private int age; getAge(); setAge();` | `record` 自动 accessor (无 setter, 不可变) | `@property` + `@x.setter` | 📁 [03_classes_and_oop.py:78](src/03_classes_and_oop.py#L78) |
| static field: `static int count = 0;` | 同左 | 类体内 `count: int = 0` | 📁 [03_classes_and_oop.py:31](src/03_classes_and_oop.py#L31) |
| `@Override toString()` | record 自动生成 | `def __repr__(self):` | 📁 [03_classes_and_oop.py:42](src/03_classes_and_oop.py#L42) |
| `@Override equals(Object o)` | record 自动生成 | `def __eq__(self, other):` | 📁 [03_classes_and_oop.py:46](src/03_classes_and_oop.py#L46) |
## 集合与泛型

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `List<String> l = new ArrayList<>();` | `var l = new ArrayList<String>();` 或 `List.of("a","b")` | `l = ["a", "b"]` | 📁 [03_classes_and_oop.py:158](src/03_classes_and_oop.py#L158) |
| `Map<K,V> m = new HashMap<>();` | `Map.of("k", "v")` (不可变) | `m = {"k": "v"}` | 📁 [02_functions_and_types.py:39](src/02_functions_and_types.py#L39) |
| `Optional<T>` | 同左 + pattern matching | `T \| None` (PEP 604) | 📁 [02_functions_and_types.py:51](src/02_functions_and_types.py#L51) |
| `T[]` 数组 | 同左 (但少用) | `list[T]` | 📁 [02_functions_and_types.py:33](src/02_functions_and_types.py#L33) |
| `IntStream.of(1,2,3).sum()` | 同左 + Stream Gatherers (JDK 22+) | `sum([1,2,3])` | 📁 [02_functions_and_types.py:35](src/02_functions_and_types.py#L35) |
| `list.stream().map(x -> x*2).collect(toList())` | `list.stream().map(x -> x*2).toList()` (JDK 16+) | `[x * 2 for x in list]` (列表推导) | 📁 [02_functions_and_types.py:65](src/02_functions_and_types.py#L65) |

## 异常与控制流

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `try { ... } catch (Exception e) { ... }` | 同左 | `try: ... except Exception as e:` | 📁 [03_classes_and_oop.py:152](src/03_classes_and_oop.py#L152) |
| `throws IOException` (checked) | 同左 (Python 没 checked exceptions) | 不区分 checked/unchecked | 📁 [07_fastapi_mini.py:97](src/07_fastapi_mini.py#L97) |
| `try-with-resources` | 同左 | `with open(...) as f:` (context manager) | 📁 [07_fastapi_mini.py:138](src/07_fastapi_mini.py#L138) |
| `switch (x) { case A: ... break; }` | `switch (x) { case A -> ...; }` (expression) | `match x: case A: ...` (3.10+) | 📁 [02_functions_and_types.py:90](src/02_functions_and_types.py#L90) |

## 异步与并发

| Java 8 老写法 | JDK 23 新写法 | Python 写法 | ref |
|---|---|---|---|
| `CompletableFuture<T>.supplyAsync(...)` | 同左 + Virtual Threads (JDK 21+) | `async def f(): ...` | 📁 [06_async_basics.py:26](src/06_async_basics.py#L26) |
| `.thenApply(f).thenCompose(g)` | 同左 | `await f()` | 📁 [06_async_basics.py:35](src/06_async_basics.py#L35) |
| `CompletableFuture.allOf(f1, f2, f3).join()` | 同左 | `await asyncio.gather(c1, c2, c3)` | 📁 [06_async_basics.py:44](src/06_async_basics.py#L44) |
| `executor.submit(...)` | `Thread.startVirtualThread(...)` (轻量级) | `asyncio.create_task(coro)` | 📁 [06_async_basics.py:68](src/06_async_basics.py#L68) |
| `future.get(1, TimeUnit.SECONDS)` | 同左 + `future.orTimeout(d)` | `await asyncio.wait_for(coro, 1.0)` | 📁 [06_async_basics.py:54](src/06_async_basics.py#L54) |
| `future.cancel(true)` | 同左 | `task.cancel()` | 📁 [06_async_basics.py:67](src/06_async_basics.py#L67) |
## Web API

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| Spring `@RestController` + `@GetMapping` | 同左 + `newVirtualThreadPerTaskExecutor` | `app=FastAPI()` + `@app.get` | 📁 [07_fastapi_mini.py:33](src/07_fastapi_mini.py#L33) |
| `@RequestBody UserDTO + @Valid` | record + Bean Validation | Pydantic `BaseModel` 自动校验 | 📁 [07_fastapi_mini.py:40](src/07_fastapi_mini.py#L40) |
| Spring Tomcat / Jetty | Helidon SE / Quarkus | uvicorn (ASGI) | 📁 [07_fastapi_mini.py:138](src/07_fastapi_mini.py#L138) |

## 包与依赖

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `package com.foo.bar;` | `module-info.java` + 包 | 含 `__init__.py` 的目录 | 📁 [04_imports_and_packages.py:37](src/04_imports_and_packages.py#L37) |
| `import com.foo.Bar;` | 同左 + JEP 476 module imports | `from foo import Bar` | 📁 [04_imports_and_packages.py:38](src/04_imports_and_packages.py#L38) |
| `pom.xml` Maven | `build.gradle.kts` Gradle | `requirements.txt` / `pyproject.toml` | 📁 [05_venv_and_pip.py:8](src/05_venv_and_pip.py#L8) |
| classpath 隔离 (JVM 内置) | module-path (JPMS) | `venv / virtualenv / uv` | 📁 [05_venv_and_pip.py:39](src/05_venv_and_pip.py#L39) |

## 字符串与格式化

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `String.format(...)` | `str.formatted(x)` | f-string | 📁 [01_hello_world.py:20](src/01_hello_world.py#L20) |
| 字符串拼接 + 显式 \n | text block | 三引号字符串 | 📁 [01_hello_world.py:1](src/01_hello_world.py#L1) |
| `"%5.2f".formatted(x)` | 同左 | `f"{x:5.2f}"` | 📁 [03_classes_and_oop.py:111](src/03_classes_and_oop.py#L111) |

## NULL 处理

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `if (x != null)` | `Optional.ofNullable(x).ifPresent` | `if x is not None:` | 📁 [02_functions_and_types.py:53](src/02_functions_and_types.py#L53) |
| `Optional.empty()` | 同左 | `None` | 📁 [02_functions_and_types.py:55](src/02_functions_and_types.py#L55) |

## 闭包与 Lambda

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `(x) -> x * x` | 同左 | `lambda x: x * x` | 📁 [02_functions_and_types.py:65](src/02_functions_and_types.py#L65) |
| 捕获 effectively final | 同左 | `nonlocal` 修改外层 | 📁 [02_functions_and_types.py:74](src/02_functions_and_types.py#L74) |

## 装饰器 / 注解

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `@Override / @Deprecated` 元数据注解 | 同左 + 自定义 Annotation | `@property / @dataclass` 功能性装饰器 | 📁 [03_classes_and_oop.py:85](src/03_classes_and_oop.py#L85) |
| AOP 通过 Spring AOP | 同左 | 装饰器一等公民 | 📁 见 PYTHON_ONLY_FEATURES.md |

## 枚举与迭代

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| `public enum Color` | 同左 record-like patterns | `class Color(Enum):` | 📁 (Ch3 工具枚举会用) |
| `for (var x : list)` | 同左 + `forEach` | `for x in list:` | 📁 [03_classes_and_oop.py:159](src/03_classes_and_oop.py#L159) |
| Iterator pattern | 同左 | `def gen(): yield x` 生成器 | 📁 见 PYTHON_ONLY_FEATURES.md |

## 可变默认参数 (Python 高频坑)

| Java 8 | JDK 23 | Python | ref |
|---|---|---|---|
| overload + `new ArrayList()` | record + `List.of()` 不可变 | Python 高频坑 用 `def f(x=None)` | 📁 [03_classes_and_oop.py:74](src/03_classes_and_oop.py#L74) |

---

## 心智模型差异 TL;DR

1. **Java 编译时强校验** — 类型/包/异常 javac 阶段挡掉; **Python 运行时检查** — 类型 hint 辅助, IDE/mypy 校验
2. **JDK 23 让 Java 接近 Python 的简洁** — record 干掉 Lombok / sealed 干掉 visitor pattern / pattern matching 干掉 instanceof 链
3. **但 Python 仍有 Java 永远学不会的** — duck typing / decorator / generator / context manager / list comprehension — 见 [PYTHON_ONLY_FEATURES.md](PYTHON_ONLY_FEATURES.md)
4. **学完此表的目标**: 看 LangChain 源码不再因 `@app.get` / `async def` / `with` 就懵

> Java 给你安全和工程化, Python 给你灵活和生产力——LLM 时代选 Python 不是因为它好, 是因为社区在那里.
