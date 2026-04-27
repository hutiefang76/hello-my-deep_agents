"""03 · 类与面向对象 — Python 的 class 比 Java 简洁但功能更野.

核心对比:
    Java                            Python
    ──────                          ──────
    public class User { ... }       class User: ...
    private int age                 self._age (约定, 不强制)
    @Data (Lombok)                  @dataclass
    public User(int x) {...}        def __init__(self, x: int): ...
    extends Animal                  class Dog(Animal): ...
    @Override                       (没有, 直接定义同名方法即可)
    static int count = 0            class 体内 count: int = 0 (类变量)
    abstract class                  ABC + @abstractmethod
    @Getter / @Setter               @property + @x.setter

Run:
    python 03_classes_and_oop.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ===== 1. 经典 class — 手写 __init__ =====
class Animal:
    """动物 — 演示构造、实例方法、特殊方法."""

    # 类变量 (相当于 Java static), 所有实例共享
    species_count: int = 0

    def __init__(self, name: str, age: int) -> None:
        # 实例变量, 加 self.
        self.name = name
        self._age = age  # 单下划线: 约定为"内部使用"
        Animal.species_count += 1

    def speak(self) -> str:
        return f"{self.name} 发出了未知的叫声"

    def __repr__(self) -> str:
        # 对应 Java 的 toString()
        return f"Animal(name={self.name!r}, age={self._age})"

    def __eq__(self, other: object) -> bool:
        # 对应 Java 的 equals()
        if not isinstance(other, Animal):
            return NotImplemented
        return self.name == other.name and self._age == other._age


# ===== 2. 继承 — 和 Java 一样, 但不写 extends =====
class Dog(Animal):
    """子类 — 重写父类方法不需要 @Override."""

    def __init__(self, name: str, age: int, breed: str) -> None:
        super().__init__(name, age)  # 类似 Java 的 super(name, age)
        self.breed = breed

    def speak(self) -> str:
        # 直接定义同名方法即覆盖父类
        return f"{self.name} ({self.breed}) 汪汪叫"


# ===== 3. dataclass — 一行代替 Lombok @Data =====
@dataclass
class User:
    """用 @dataclass 自动生成 __init__/__repr__/__eq__, 比 Lombok 更内置."""

    id: str
    name: str
    age: int = 0
    tags: list[str] = field(default_factory=list)  # 可变默认值必须用 factory


# ===== 4. @property — 对应 Java getter/setter =====
class BankAccount:
    """演示 property: 调用方写 acc.balance 像访问字段, 实际上跑了一个方法."""

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        """getter — acc.balance 触发这里."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """setter — acc.balance = 100 触发这里."""
        if value < 0:
            raise ValueError("余额不能为负")
        self._balance = value

    def deposit(self, amount: float) -> None:
        self._balance += amount


# ===== 5. 抽象类 — Java 的 abstract class =====
class Shape(ABC):
    """抽象类 — 不能实例化, 子类必须实现 area()."""

    @abstractmethod
    def area(self) -> float:
        """子类必须实现 — 否则实例化会报错."""

    def describe(self) -> str:
        # 普通方法 — 子类可以继承不重写
        return f"{type(self).__name__} 的面积是 {self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius * self.radius


class Rectangle(Shape):
    def __init__(self, w: float, h: float) -> None:
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h


def main() -> None:
    print("--- 1. Animal & Dog (经典 class + 继承) ---")
    a1 = Animal("Tom", 3)
    d1 = Dog("Buddy", 5, "Golden")
    print(f"a1 = {a1}")
    print(f"d1 = {d1}")
    print(f"a1.speak() = {a1.speak()}")
    print(f"d1.speak() = {d1.speak()}")
    print(f"Animal.species_count = {Animal.species_count}")
    print(f"a1 == Animal('Tom', 3) = {a1 == Animal('Tom', 3)}")

    print("\n--- 2. User (dataclass — Lombok @Data 等价) ---")
    u = User(id="u1", name="Alice", age=30, tags=["admin", "vip"])
    print(f"u = {u}")
    print(f"u.name = {u.name}")

    print("\n--- 3. BankAccount (property 演示 getter/setter) ---")
    acc = BankAccount("Frank", 1000.0)
    print(f"acc.balance = {acc.balance}")  # 看起来访问字段, 其实调用了 getter
    acc.deposit(500)
    print(f"acc.balance after deposit(500) = {acc.balance}")
    try:
        acc.balance = -100
    except ValueError as e:
        print(f"setter 拦截负数: {e}")

    print("\n--- 4. Shape 抽象类 + 多态 ---")
    shapes: list[Shape] = [Circle(5), Rectangle(3, 4)]
    for s in shapes:
        print(s.describe())

    try:
        Shape()  # 抽象类不能实例化
    except TypeError as e:
        print(f"抽象类拒绝实例化: {e}")


if __name__ == "__main__":
    main()
