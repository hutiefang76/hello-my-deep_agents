import java.util.List;

/**
 * 等价 Python: src/04_imports_and_packages.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Java                                          Python
 *   ────                                          ──────
 *   package com.foo.bar;                          文件放在 foo/bar/, 加 __init__.py
 *   import com.foo.bar.Baz;                       from foo.bar import Baz
 *   import com.foo.bar.*;                          from foo.bar import *  (不推荐)
 *   import static com.foo.Util.METHOD;            from foo.util import METHOD
 *   classpath / module-path                       sys.path
 *   module-info.java (JPMS)                       __init__.py + __all__
 * </pre>
 *
 * <p>Java 包 vs Python 包的根本差异:
 * <ul>
 *   <li>Java: 编译时强制目录结构 = package 声明, 编译器报错</li>
 *   <li>Python: 运行时按 sys.path 查找, 任何带 __init__.py 的目录都成包</li>
 *   <li>JDK 9+ 引入 JPMS (module-info.java) 加了一层模块封装, 比 Python 更严格</li>
 *   <li>JDK 23 预览 JEP 476: Module Import Declarations (一行导入整个模块)</li>
 * </ul>
 *
 * <p>本文件演示"一个文件内"能玩的 import 形式. 真实多文件 package 演示在
 * Python 这边的 _demo_package/ — Java 这边为了纯单文件编译, 把 demo 工具
 * 写成 nested class.
 */
class ImportsAndPackages {

    /**
     * 演示用嵌套类 — 模拟 Python 的 _demo_package.math_utils.
     * 真实项目中应放在 com.example.demo.MathUtils.java 独立文件.
     */
    static final class MathUtils {
        static final double PI = 3.14159;

        static int add(final int a, final int b) {
            return a + b;
        }

        static int multiply(final int a, final int b) {
            return a * b;
        }

        private MathUtils() {} // 工具类不允许实例化, Java 习惯
    }

    /** 演示用嵌套类 — 模拟 Python 的 _demo_package.string_utils. */
    static final class StringUtils {

        /** Java 没有 Python 切片, 用 StringBuilder.reverse() 等价. */
        static String reverse(final String s) {
            return new StringBuilder(s).reverse().toString();
        }

        /** user_name → userName. */
        static String snakeToCamel(final String s) {
            final String[] parts = s.split("_");
            if (parts.length == 0) {
                return "";
            }
            // Stream API + reduce — 等价 Python 的 parts[0] + "".join(p.title() for p in parts[1:])
            final var head = parts[0];
            final var tail = java.util.Arrays.stream(parts, 1, parts.length)
                    .map(p -> Character.toUpperCase(p.charAt(0)) + p.substring(1))
                    .reduce("", String::concat);
            return head + tail;
        }

        private StringUtils() {}
    }

    static void showPaths() {
        // Java 的 classpath / module path — 等价 Python 的 sys.path
        System.out.println("--- Java 的 classpath / module-path (等价 Python sys.path) ---");
        final String classpath = System.getProperty("java.class.path");
        // 拆开打印前 5 项
        final var paths = classpath.split(System.getProperty("path.separator"));
        for (int i = 0; i < Math.min(5, paths.length); i++) {
            System.out.println("  [%d] %s".formatted(i + 1, paths[i]));
        }
        System.out.println("  ... 共 %d 项".formatted(paths.length));
    }

    static void showModuleInfo() {
        System.out.println("\n--- 当前类元信息 (Java 没有 module-level __name__/__file__) ---");
        System.out.println("  Class.getName()             = " + ImportsAndPackages.class.getName());
        System.out.println("  Class.getSimpleName()       = " + ImportsAndPackages.class.getSimpleName());
        System.out.println("  Package                     = " + ImportsAndPackages.class.getPackage());
        // Java 没有"被 import 时不执行" 的概念 — main 方法只在 java HelloWorld 时被调用
        // 任何"被 import 进来"的 class 都不会自动执行任何代码 (除非 static block)
    }

    static void callDemoUtils() {
        System.out.println("\n--- 调用嵌套工具类 (等价 _demo_package) ---");
        System.out.println("MathUtils.add(3, 4)              = " + MathUtils.add(3, 4));
        System.out.println("MathUtils.PI                     = " + MathUtils.PI);
        System.out.println("StringUtils.reverse('hello')     = " + StringUtils.reverse("hello"));
        System.out.println("StringUtils.snakeToCamel(...)    = " + StringUtils.snakeToCamel("user_name"));
    }

    public static void main(final String[] args) {
        showPaths();
        showModuleInfo();
        callDemoUtils();

        // text block + List.of — 等价 Python 多行字符串 + list
        final List<String> keyPoints = List.of(
                "1. Java: 一个文件 = 一个 public class (文件名严格匹配)",
                "2. Python: 一个 .py = 一个 module (无强制类名)",
                "3. Java: package 必须匹配目录结构, 编译器强校验",
                "4. Python: package = 含 __init__.py 的目录 (运行时校验)",
                "5. Java: classpath/module-path 是编译期+启动期, 改了要重启",
                "6. Python: sys.path 是运行时可改的 list, 极其灵活 (但易乱)"
        );
        System.out.println("\n--- 关键点 ---");
        keyPoints.forEach(System.out::println);
    }
}
