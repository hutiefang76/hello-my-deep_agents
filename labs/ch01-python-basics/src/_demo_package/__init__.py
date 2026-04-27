"""_demo_package — 演示用 Python 包.

含 __init__.py 的目录就是一个 package.
文件顶部下划线表示"内部演示用, 不打算被外部引用".
"""

# 在 __init__.py 里 export 出来的东西, 可以被 from _demo_package import X 直接用
from .math_utils import PI, add  # noqa: F401
from .string_utils import reverse, snake_to_camel  # noqa: F401

__all__ = ["PI", "add", "reverse", "snake_to_camel"]
__version__ = "0.1.0"
