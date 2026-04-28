import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * 等价 Python: src/03_classes_and_oop.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Java 8 老写法                           JDK 23 新写法                      Python 写法
 *   ─────────────                           ──────────────                    ────────────
 *   POJO + getter/setter (Lombok @Data)     record User(...)                  &#64;dataclass class User
 *   abstract class + 子类                    sealed interface + permits         ABC + &#64;abstractmethod
 *   instanceof + cast                        pattern matching switch            isinstance + duck typing
 *   重写 + &#64;Override                          同左 (但子类隐式继承)               直接定义同名方法
 *   private int age + getAge()              record 自带 accessor               &#64;property
 * </pre>
 *
 * <p>JDK 23 特性使用:
 * <ul>
 *   <li>{@code record} — 替代 Lombok &#64;Data / Python &#64;dataclass</li>
 *   <li>{@code sealed interface} — 限定子类范围 (Python 没有等价, 用 Protocol/ABC 模拟)</li>
 *   <li>Pattern matching switch — 比 instanceof 链更优雅</li>
 *   <li>{@code var} — 局部类型推断</li>
 * </ul>
 */
class ClassesAndOop {

    // ===== 1. 经典 class — 手写 ctor (Python 的 __init__) =====
    /** 动物 — 演示传统 class. JDK 23 仍保留, 但有状态/继承时才用. */
    static class Animal {

        /** 类变量 (Java static field) — 等价 Python class 体内的 species_count. */
        static int speciesCount = 0;

        protected final String name;
        protected final int age;

        Animal(final String name, final int age) {
            this.name = name;
            this.age = age;
            speciesCount++;
        }

        /** Python 直接定义同名方法重写, Java 写 &#64;Override 增强可读性. */
        public String speak() {
            return "%s 发出了未知的叫声".formatted(name);
        }

        /** 等价 Python 的 __repr__. */
        @Override
        public String toString() {
            return "Animal(name=%s, age=%d)".formatted(name, age);
        }

        /** 等价 Python 的 __eq__. */
        @Override
        public boolean equals(final Object other) {
            return other instanceof Animal a && Objects.equals(name, a.name) && age == a.age;
        }

        @Override
        public int hashCode() {
            return Objects.hash(name, age);
        }
    }

    // ===== 2. 继承 — extends 关键字 (Python 是 class Dog(Animal):) =====
    static class Dog extends Animal {

        private final String breed;

        Dog(final String name, final int age, final String breed) {
            super(name, age);
            this.breed = breed;
        }

        @Override
        public String speak() {
            return "%s (%s) 汪汪叫".formatted(name, breed);
        }
    }

    // ===== 3. record — JDK 14+, 一行干掉 Lombok @Data + Python @dataclass =====
    /**
     * 用户 — record 自动生成 ctor / accessor / equals / hashCode / toString.
     * 等价 Python {@code @dataclass class User: id: str; name: str; age: int = 0}.
     */
    record User(String id, String name, int age, List<String> tags) {
        /** Compact constructor — 校验 + 防御性拷贝 (Python @dataclass 也支持 __post_init__). */
        public User {
            Objects.requireNonNull(id, "id 不能为空");
            tags = List.copyOf(tags); // 不可变拷贝, 防止外部篡改
        }

        /** 简化 ctor — Java 没有"默认参数", 用 overload 模拟 Python age=0, tags=[]. */
        public User(final String id, final String name) {
            this(id, name, 0, List.of());
        }
    }

    // ===== 4. record 也能做 getter (没 setter, record 是不可变的) =====
    /** 银行账户 — 演示 record 不可变 + 演化方法返回新实例 (函数式风格). */
    record BankAccount(String owner, double balance) {

        public BankAccount {
            if (balance < 0) {
                throw new IllegalArgumentException("余额不能为负");
            }
        }

        /** 存款返回新 record (Python @property setter 等价是直接 mutate, 这里更函数式). */
        public BankAccount deposit(final double amount) {
            return new BankAccount(owner, balance + amount);
        }
    }

    // ===== 5. sealed interface — JDK 17+, 比 Python ABC 更严格 (限定子类) =====
    /**
     * 形状 — sealed interface 限定只有 Circle/Rectangle 实现.
     * Python 的 ABC 只能限定"必须实现哪些方法", 限定不了"谁能继承".
     */
    sealed interface Shape permits Circle, Rectangle {

        double area();

        default String describe() {
            return "%s 的面积是 %.2f".formatted(this.getClass().getSimpleName(), area());
        }
    }

    record Circle(double radius) implements Shape {
        @Override
        public double area() {
            return Math.PI * radius * radius;
        }
    }

    record Rectangle(double w, double h) implements Shape {
        @Override
        public double area() {
            return w * h;
        }
    }

    // ===== 6. Pattern matching switch on sealed type — JDK 21+ stable =====
    /** 编译器知道 sealed 的所有子类, 不写 default 都不会警告 (穷尽性检查). */
    static String classify(final Shape shape) {
        return switch (shape) {
            case Circle c -> "圆形 半径=%.2f".formatted(c.radius());
            case Rectangle r -> "矩形 %.2fx%.2f".formatted(r.w(), r.h());
        };
    }

    public static void main(final String[] args) {
        System.out.println("--- 1. Animal & Dog (经典 class + 继承) ---");
        final var a1 = new Animal("Tom", 3);
        final var d1 = new Dog("Buddy", 5, "Golden");
        System.out.println("a1 = " + a1);
        System.out.println("d1 = " + d1);
        System.out.println("a1.speak() = " + a1.speak());
        System.out.println("d1.speak() = " + d1.speak());
        System.out.println("Animal.speciesCount = " + Animal.speciesCount);
        System.out.println("a1.equals(new Animal('Tom', 3)) = " + a1.equals(new Animal("Tom", 3)));

        System.out.println("\n--- 2. User (record — Lombok @Data 等价) ---");
        final var tags = new ArrayList<String>();
        tags.add("admin");
        tags.add("vip");
        final var u = new User("u1", "Alice", 30, tags);
        System.out.println("u = " + u);
        System.out.println("u.name() = " + u.name());

        System.out.println("\n--- 3. BankAccount (record 不可变 + 函数式演化) ---");
        var acc = new BankAccount("Frank", 1000.0);
        System.out.println("acc.balance() = " + acc.balance());
        acc = acc.deposit(500); // 返回新实例
        System.out.println("acc.balance() after deposit(500) = " + acc.balance());
        try {
            new BankAccount("Frank", -100);
        } catch (IllegalArgumentException e) {
            System.out.println("compact ctor 拦截负数: " + e.getMessage());
        }

        System.out.println("\n--- 4. Shape sealed + pattern matching ---");
        final List<Shape> shapes = List.of(new Circle(5), new Rectangle(3, 4));
        for (final var s : shapes) {
            System.out.println(s.describe() + " | " + classify(s));
        }
    }
}
