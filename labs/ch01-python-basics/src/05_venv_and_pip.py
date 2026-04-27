"""05 · 虚拟环境与依赖管理 — pip / venv vs Maven / Gradle.

对照:
    Java/Maven                       Python/pip
    ────────                         ──────────
    pom.xml                          requirements.txt 或 pyproject.toml
    mvn install                      pip install -r requirements.txt
    ~/.m2/repository                 ~/.pip/cache (默认全局) 或 .venv/lib/...
    classpath 隔离                   虚拟环境隔离 (venv / virtualenv / uv)
    mvn package                      python -m build
    Maven Central                    PyPI

为什么需要虚拟环境:
    Java 通过 classpath 隔离不同项目的依赖, Python 没有 classpath 概念.
    所以必须用 venv 给每个项目建独立的 site-packages 目录, 否则全局污染.

Run:
    python 05_venv_and_pip.py    # 此脚本只打印当前环境信息, 不实际装包
"""

from __future__ import annotations

import shutil
import sys
import sysconfig
from pathlib import Path


def main() -> None:
    print("=" * 60)
    print("Python 虚拟环境与依赖管理速查")
    print("=" * 60)

    print("\n--- 当前 Python ---")
    print(f"  Version       : {sys.version.split()[0]}")
    print(f"  Executable    : {sys.executable}")
    print(f"  Prefix        : {sys.prefix}")
    print(f"  Base prefix   : {sys.base_prefix}")
    in_venv = sys.prefix != sys.base_prefix
    print(f"  In venv?      : {in_venv}  ({'[YES]' if in_venv else '[WARN] 全局环境, 建议先建 venv'})")

    print("\n--- site-packages (依赖装在这里) ---")
    site_pkg = sysconfig.get_paths().get("purelib", "")
    print(f"  {site_pkg}")
    if Path(site_pkg).exists():
        # 列出当前环境装了哪些 (粗略)
        try:
            pkgs = [p.name for p in Path(site_pkg).iterdir() if p.is_dir() and not p.name.startswith("_")]
            print(f"  已装 {len(pkgs)} 个 package, 前 10 个:")
            for p in pkgs[:10]:
                print(f"    - {p}")
        except Exception as e:
            print(f"  扫描失败: {e}")

    print("\n--- 关键命令速查 ---")
    print("  # 1. 建虚拟环境")
    print("  python -m venv .venv")
    print()
    print("  # 2. 激活")
    print("  source .venv/bin/activate          # macOS/Linux")
    print("  .venv\\Scripts\\activate              # Windows")
    print()
    print("  # 3. 装单包")
    print("  pip install langchain")
    print()
    print("  # 4. 从 requirements.txt 批量装")
    print("  pip install -r requirements.txt")
    print()
    print("  # 5. 导出当前环境的依赖")
    print("  pip freeze > requirements.txt")
    print()
    print("  # 6. 退出虚拟环境")
    print("  deactivate")

    print("\n--- 推荐替代品 (现代化) ---")
    print("  uv          # Rust 实现, 比 pip 快 10-100x, 已成主流")
    print("              # https://github.com/astral-sh/uv")
    print("  poetry      # 类似 npm, 有 lockfile, 适合 lib 开发")
    print("  pipx        # 全局装 CLI 工具的隔离环境")

    # 演示: 检测一下当前是否有 uv (如果用户已装会很爽)
    uv_path = shutil.which("uv")
    if uv_path:
        print(f"\n  [OK] 检测到 uv: {uv_path}")
    else:
        print("\n  [TIP] 没装 uv? curl -LsSf https://astral.sh/uv/install.sh | sh")


if __name__ == "__main__":
    main()
