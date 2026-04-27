# Ch 1 · Python 基础（针对 Java 工程师）

> 7 个脚本带你从 `public static void main` 切换到 `if __name__ == "__main__":`

## 学完能力

- 能写函数、类、装饰器、async 函数
- 能管理虚拟环境、装依赖
- 能写一个最简 FastAPI Web 服务（对标 Spring Boot @RestController）
- 看懂后续 lab 的所有 Python 代码

## 前置依赖

- Python 3.10+
- pip / venv

```bash
# 进入仓库根, 激活虚拟环境
cd ../..
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 脚本列表

| 脚本 | 主题 | Java 对照 | 跑法 |
|---|---|---|---|
| `01_hello_world.py` | 打印 + 编码 + main 入口 | `public static void main` | `python src/01_hello_world.py` |
| `02_functions_and_types.py` | 函数、默认参数、类型提示 | 方法签名、泛型、`Optional<T>` | `python src/02_functions_and_types.py` |
| `03_classes_and_oop.py` | 类、继承、`@dataclass`、`@property` | POJO、Lombok、getter/setter | `python src/03_classes_and_oop.py` |
| `04_imports_and_packages.py` | 模块、包、`__init__.py`、相对导入 | package、import | `python src/04_imports_and_packages.py` |
| `05_venv_and_pip.py` | venv、pip、requirements.txt | Maven/Gradle、pom.xml | `python src/05_venv_and_pip.py` |
| `06_async_basics.py` | `async/await`、并发任务 | CompletableFuture、@Async | `python src/06_async_basics.py` |
| `07_fastapi_mini.py` | FastAPI、路由、Pydantic | Spring Boot、@RestController | `python src/07_fastapi_mini.py` |

## 一键验证

```bash
bash verify.sh
```

预期输出：每个脚本输出 `✅ PASSED`。

## Java vs Python 速查表

| 概念 | Java | Python |
|---|---|---|
| 入口 | `public static void main(String[] args)` | `if __name__ == "__main__":` |
| 包导入 | `import com.foo.Bar;` | `from foo import Bar` |
| 类型 | `String name = "x"` | `name: str = "x"` (可选) |
| 集合 | `List<String>` | `list[str]` |
| 可空 | `Optional<String>` | `str | None` |
| 数据类 | `@Data class User { ... }` | `@dataclass class User: ...` |
| 异步 | `CompletableFuture` | `async def` + `await` |
| Web | Spring Boot `@RestController` | FastAPI `@app.get()` |
| 依赖 | `pom.xml` | `requirements.txt` |
| 构建 | `mvn package` | `python -m build` |
| 运行 | `java -jar app.jar` | `python app.py` |

## 下一步

学完 Ch1 → 直接进 [Ch 2 LangChain 基础](../ch02-langchain-basics/)
