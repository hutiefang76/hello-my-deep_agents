"""string_utils — 演示包内字符串工具."""


def reverse(s: str) -> str:
    """字符串反转 — Python 切片语法很优雅: s[::-1]."""
    return s[::-1]


def snake_to_camel(s: str) -> str:
    """user_name → userName."""
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])
