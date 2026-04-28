import java.util.List;

/**
 * 等价 Python: src/05_venv_and_pip.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Java/Maven                          Python/pip
 *   ──────────                          ──────────
 *   pom.xml                             requirements.txt 或 pyproject.toml
 *   build.gradle / build.gradle.kts     pyproject.toml (PEP 621)
 *   mvn install / gradle build          pip install -r requirements.txt
 *   ~/.m2/repository                    ~/.pip/cache 或 .venv/lib/...
 *   classpath / module-path 隔离         虚拟环境隔离 (venv / virtualenv / uv)
 *   mvn package                         python -m build
 *   Maven Central                       PyPI
 *   SDKMAN! / asdf (JDK 版本管理)        pyenv / uv (Python 版本管理)
 *   IDE 自动 import                       pip install + import
 * </pre>
 *
 * <p>为什么 Python 需要虚拟环境而 Java 不需要:
 * <ul>
 *   <li>Java: 每个项目自带 classpath / module-path, 启动 JVM 时指定, 天然隔离</li>
 *   <li>Python: 默认全局 site-packages, 没显式隔离, 不同项目装不同版本会冲突</li>
 *   <li>所以 Python 必须用 venv 给每个项目建独立的 site-packages 目录</li>
 * </ul>
 *
 * <p>JDK 23 特性使用:
 * <ul>
 *   <li>{@code text block} — 命令速查的多行字符串</li>
 *   <li>{@code var} — 局部类型推断</li>
 *   <li>{@code List.of} — 不可变集合字面量 (JDK 9+)</li>
 * </ul>
 *
 * <p>本文件不实际安装包, 只打印当前 JVM 环境信息 + Maven/Python 速查.
 */
class VenvAndPip {

    public static void main(final String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Java 依赖管理速查 (对照 Python venv/pip)");
        System.out.println("=".repeat(60));

        // ===== 1. 当前 JVM 信息 (等价 Python 的 sys.version) =====
        System.out.println("\n--- 当前 JVM ---");
        System.out.println("  Java Version  : " + System.getProperty("java.version"));
        System.out.println("  JVM           : " + System.getProperty("java.vm.name"));
        System.out.println("  JAVA_HOME     : " + System.getProperty("java.home"));
        // Java 没有"虚拟环境"概念, 但有 JAVA_HOME 切换 JDK 版本
        // SDKMAN! 是 Java 生态的 pyenv 等价物
        System.out.println("  module-path?  : " + (System.getProperty("jdk.module.path") != null));

        // ===== 2. classpath / module-path (Java 的"site-packages") =====
        System.out.println("\n--- classpath (Java 的 site-packages) ---");
        final var classpath = System.getProperty("java.class.path", "");
        final var entries = classpath.split(System.getProperty("path.separator"));
        System.out.println("  共 %d 项, 前 5 项:".formatted(entries.length));
        for (int i = 0; i < Math.min(5, entries.length); i++) {
            System.out.println("    - " + entries[i]);
        }

        // ===== 3. Maven / Gradle 命令速查 =====
        final var mavenCheatsheet = """

                --- Maven 命令速查 (对照 pip) ---
                  # 1. 创建项目骨架
                  mvn archetype:generate -DgroupId=com.example -DartifactId=demo

                  # 2. 装依赖 (会下载到 ~/.m2/repository)
                  mvn install                       # 等价: pip install -r requirements.txt

                  # 3. 编译 + 跑测试
                  mvn package                       # 等价: python -m build

                  # 4. 跑主类
                  mvn exec:java -Dexec.mainClass=com.example.App

                  # 5. 查依赖树
                  mvn dependency:tree               # 等价: pip show / pipdeptree
                """;
        System.out.println(mavenCheatsheet);

        final var gradleCheatsheet = """
                --- Gradle 命令速查 (对照 pip + 现代化工具) ---
                  gradle init                       # 创建项目
                  ./gradlew build                   # 编译+测试+打包
                  ./gradlew run                     # 跑 application 插件下的 main
                  ./gradlew dependencies            # 查依赖树
                """;
        System.out.println(gradleCheatsheet);

        // ===== 4. JDK 版本管理 (Python pyenv 等价) =====
        final List<String> jdkVersionTools = List.of(
                "SDKMAN!     # https://sdkman.io  Java 生态最流行的版本管理 (= pyenv)",
                "asdf        # https://asdf-vm.com 多语言版本管理 (Python/Node/Java 都管)",
                "jenv        # macOS 老牌 Java 版本切换工具",
                "Coursier    # Scala 社区出品, 也支持 JVM 通用"
        );
        System.out.println("--- JDK 版本管理 (Python 的 pyenv 等价) ---");
        jdkVersionTools.forEach(t -> System.out.println("  " + t));

        // ===== 5. 一键对照表 =====
        final var comparison = """

                --- 速查对照表 ---
                  概念                  Java                            Python
                  ────                  ────                            ──────
                  依赖描述文件           pom.xml / build.gradle          requirements.txt / pyproject.toml
                  下载缓存               ~/.m2/repository                ~/.pip/cache
                  项目隔离               classpath / module-path         venv / virtualenv
                  仓库                  Maven Central                   PyPI
                  锁文件                pom.xml (固定版本)              poetry.lock / uv.lock
                  现代化工具             Gradle / Maven Wrapper          uv (Rust 写的, 10-100x 快)
                  CLI 工具隔离           jbang                           pipx
                """;
        System.out.println(comparison);
    }
}
