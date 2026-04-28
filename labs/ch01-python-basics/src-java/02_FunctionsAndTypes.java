import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.IntSupplier;
import java.util.stream.IntStream;

/**
 * 等价 Python: src/02_functions_and_types.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Java 8 老写法                       JDK 23 新写法                          Python 写法
 *   ─────────────                       ──────────────                        ────────────
 *   public String foo(int x)            String foo(int x)                     def foo(x: int) -> str
 *   List&lt;String&gt; bar()                  返回 record / 不变                     def bar() -> list[str]
 *   Optional&lt;User&gt; find(id)             Optional&lt;User&gt; (or sealed result)     def find(id) -> User | None
 *   void baz(int... args)               void baz(int... args)                 def baz(*args: int)
 *   Map&lt;String, Object&gt; kv               record 或 Map.of                      **kwargs
 *   方法重载 (overload)                   仍是 overload (Python 不支持)           默认参数模拟
 *   Function&lt;T,R&gt; (Java 8 lambda)        同左 + Stream API                      def / lambda
 * </pre>
 *
 * <p>JDK 23 特性使用:
 * <ul>
 *   <li>{@code record} — 多返回值 (Python tuple 等价)</li>
 *   <li>{@code var} — 局部类型推断</li>
 *   <li>Stream API — 替代命令式 for 循环</li>
 *   <li>Pattern matching {@code instanceof}</li>
 * </ul>
 */
class FunctionsAndTypes {

    // ===== 1. 基础函数 =====
    static int add(final int x, final int y) {
        return x + y;
    }

    // ===== 2. 默认参数 — Java 没有, 必须 overload (Python 一行搞定) =====
    static String greet(final String name) {
        return greet(name, "Hello");
    }

    static String greet(final String name, final String greeting) {
        return "%s, %s!".formatted(greeting, name);
    }

    // ===== 3. 可变参数 — Python 的 *args =====
    static int sumAll(final int... numbers) {
        return IntStream.of(numbers).sum();
    }

    // ===== 4. 关键字参数 — Java 没有原生 **kwargs, 用 Map 模拟 =====
    static Map<String, String> buildUser(final Map<String, String> attrs) {
        return new HashMap<>(attrs);
    }

    // ===== 5. 多返回值 — JDK 23 用 record 替代 Python tuple =====
    /** 商和余数的多元返回 — 等价 Python 的 tuple[int, int]. */
    record DivMod(int quotient, int remainder) {}

    static DivMod divmodPair(final int a, final int b) {
        return new DivMod(a / b, a % b);
    }

    // ===== 6. 可空类型 — Java 用 Optional, Python 用 X | None =====
    /** 用户记录 — 等价 Python 的 dict[str, str], 但有类型. */
    record User(String id, String role) {}

    static Optional<User> findUser(final String userId) {
        return "alice".equals(userId)
                ? Optional.of(new User("alice", "admin"))
                : Optional.empty();
    }

    // ===== 7. 高阶函数 — Java 8 Function<T,R>, Python 函数本身就是一等公民 =====
    static <T, R> R apply(final Function<T, R> func, final T value) {
        return func.apply(value);
    }

    // ===== 8. lambda — Java 8 起就有, JDK 23 没变, 但 Stream 用起来更顺 =====
    static final Function<Integer, Integer> SQUARE = x -> x * x;

    // ===== 9. 闭包 — Java lambda 只能捕获 effectively final, 想要可变状态需 wrap =====
    static IntSupplier makeCounter(final int start) {
        // 用单元素数组绕过 effectively final 限制 (Python 用 nonlocal)
        final int[] count = {start};
        return () -> ++count[0];
    }

    public static void main(final String[] args) {
        System.out.println("add(2, 3)             = " + add(2, 3));
        System.out.println("greet('Alice')        = " + greet("Alice"));
        System.out.println("greet('Bob', '你好')  = " + greet("Bob", "你好"));
        System.out.println("sumAll(1..5)          = " + sumAll(1, 2, 3, 4, 5));

        // Map.of 是 Java 9+ 的不可变 Map 字面量, 类似 Python dict literal
        final var user = buildUser(Map.of("name", "alice", "role", "admin"));
        System.out.println("buildUser(...)        = " + user);

        // record 析构 — JDK 21+ 支持 record pattern
        final DivMod dm = divmodPair(17, 5);
        System.out.println("divmodPair(17, 5)     = " + dm);

        // pattern matching switch — JDK 21+ stable
        final var found = findUser("alice");
        System.out.println("findUser('alice')     = " + describeOptional(found));
        System.out.println("findUser('zzz')       = " + describeOptional(findUser("zzz")));

        System.out.println("apply(SQUARE, 7)      = " + apply(SQUARE, 7));

        final var counter = makeCounter(10);
        System.out.println("counter() x3          = "
                + counter.getAsInt() + ", " + counter.getAsInt() + ", " + counter.getAsInt());

        // Stream API — Python 列表推导式的 Java 等价
        final List<Integer> squared = List.of(1, 2, 3, 4, 5).stream()
                .map(SQUARE)
                .toList();
        System.out.println("squared (Stream)      = " + squared);
    }

    /** Pattern matching switch (JDK 21+ stable) — 比 Optional.map 更直观. */
    static String describeOptional(final Optional<User> maybeUser) {
        return switch (maybeUser.orElse(null)) {
            case null -> "<not found>";
            case User u -> u.toString();
        };
    }
}
