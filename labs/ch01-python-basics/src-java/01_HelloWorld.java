/**
 * 等价 Python: src/01_hello_world.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <ul>
 *   <li>Java 入口: {@code public static void main(String[] args)}</li>
 *   <li>Python 入口: {@code if __name__ == "__main__":}</li>
 *   <li>Java 文件 = 一个 Class, Python 文件 = 一个 Module (天然脚本)</li>
 * </ul>
 *
 * <p>JDK 23 特性使用:
 * <ul>
 *   <li>{@code text block} (三引号字符串) — 等价 Python 的 docstring/多行字符串</li>
 *   <li>{@code var} 局部类型推断 — 等价 Python 的 {@code name = "x"} (无需写类型)</li>
 * </ul>
 *
 * <p>编译运行:
 * <pre>
 * javac -d /tmp/javatest 01_HelloWorld.java
 * java -cp /tmp/javatest HelloWorld
 * </pre>
 *
 * <p>注意: Java 文件名带数字前缀 (01_) 是教学排序需要, 类名用 {@code HelloWorld}
 * (Java 标识符不能以数字开头). 所以类是 package-private, 不加 public.
 */
class HelloWorld {

    /**
     * 打招呼 — 等价 Python 的 {@code def greet(name: str) -> str}.
     *
     * @param name 姓名
     * @return 问候语
     */
    static String greet(final String name) {
        // Java 15+ text block + String.formatted() 是 Python f-string 的等价
        return "Hello, %s!".formatted(name);
    }

    /**
     * Python 用 main() 函数封装入口逻辑, Java 直接用 main 方法.
     *
     * @param args 命令行参数 (等价 Python 的 sys.argv[1:])
     */
    public static void main(final String[] args) {
        // Python 3 默认 UTF-8, Java 也从 JEP 400 (Java 18) 起默认 UTF-8
        System.out.println("Hello, hello-my-deep_agents! 你好, 深度智能体!");

        // var 局部类型推断 (JDK 10+) — 等价 Python 的隐式类型
        var greeting1 = greet("DeepAgents");
        var greeting2 = greet("Java 工程师");
        System.out.println(greeting1);
        System.out.println(greeting2);

        // text block — 等价 Python 的三引号字符串
        final String banner = """
                ===== 关键认知 =====
                1. Python 文件天然就是脚本, 直接 python xxx.py 跑
                2. Java 必须有 class + main 方法 + 编译成 .class
                3. Python 的 __name__ == "__main__" 是为了区分"被运行"和"被 import"
                4. Java 没这个困扰 — 一个文件只能被 import (作为类), 不能被"运行成脚本"
                ====================
                """;
        System.out.println(banner);

        // Java 没有直接对应 __name__ / __file__ 的概念, 需要靠反射
        System.out.println("Class name = " + HelloWorld.class.getName());
        System.out.println("args.length = " + args.length);
    }
}
