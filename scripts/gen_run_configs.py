"""gen_run_configs.py — 批量生成 PyCharm Run Configurations.

为 labs/ 下每个 .py 脚本生成 .run/*.run.xml, 让 PyCharm 自动识别.
跑一次, 67+ 个 run config 全部就位 — 不用手动 New Run Config.

PyCharm 要求:
- 项目 SDK 已配 (项目根 .venv)
- .run/ 目录会被 PyCharm 自动扫描 (从 2020.3+)

用法:
    python scripts/gen_run_configs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / ".run"
LABS_DIR = REPO_ROOT / "labs"

# 已知不需要 run config 的:
SKIP_FILES = {
    "_corpus.py",          # Ch10 helper, 不直接跑
    "rag_pipeline_helpers.py",  # Ch4.2.3 helper
    "common_search.py",    # Ch3 helper
    "cs_kb.py",            # Ch9 helper
}

# Run Config XML 模板
TEMPLATE = """<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="{name}" type="PythonConfigurationType" factoryName="Python" folderName="{folder}">
    <module name="{module}" />
    <option name="ENV_FILES" value="$PROJECT_DIR$/.env" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="PYTHONIOENCODING" value="utf-8" />
      <env name="PYTHONUNBUFFERED" value="1" />
      <env name="PYTHONPATH" value="$PROJECT_DIR$" />
    </envs>
    <option name="SDK_HOME" value="" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="true" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <EXTENSION ID="PythonCoverageRunConfigurationExtension" runner="coverage.py" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/{script_path}" />
    <option name="PARAMETERS" value="" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="true" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
"""


def script_to_config_filename(script: Path) -> str:
    """labs/ch02-langchain-basics/src/02_prompt_template.py
       → ch02_02_prompt_template.run.xml"""
    parts = script.relative_to(LABS_DIR).parts
    # parts = ("ch02-langchain-basics", "src", "02_prompt_template.py")
    chapter = parts[0].split("-")[0]  # "ch02"
    stem = script.stem  # "02_prompt_template"
    return f"{chapter}_{stem}.run.xml"


def script_to_display_name(script: Path) -> str:
    """labs/ch02-langchain-basics/src/02_prompt_template.py
       → ch02 · 02_prompt_template"""
    parts = script.relative_to(LABS_DIR).parts
    chapter = parts[0].split("-")[0]
    stem = script.stem
    return f"{chapter} · {stem}"


def script_to_folder_name(script: Path) -> str:
    """labs/ch04-2-1-memory/src/01_short_term.py → ch04-2-1 memory"""
    parts = script.relative_to(LABS_DIR).parts
    chapter_dir = parts[0]
    # ch02-langchain-basics → "ch02 langchain"
    bits = chapter_dir.split("-", 1)
    if len(bits) == 2:
        return f"{bits[0]} {bits[1].replace('-', ' ')}"
    return chapter_dir


def detect_module_name() -> str:
    """从 .idea/modules.xml 读 module name; 拿不到就用目录名."""
    modules_xml = REPO_ROOT / ".idea" / "modules.xml"
    if modules_xml.exists():
        text = modules_xml.read_text(encoding="utf-8")
        # 简单提取 .iml 文件名
        import re
        match = re.search(r'/([^/]+)\.iml"', text)
        if match:
            return match.group(1)
    return REPO_ROOT.name


def main() -> int:
    if not LABS_DIR.exists():
        print(f"❌ labs/ not found at {LABS_DIR}", file=sys.stderr)
        return 1

    RUN_DIR.mkdir(exist_ok=True)
    module = detect_module_name()
    # Force UTF-8 stdout on Windows GBK terminals
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print(f"[*] Module name: {module}")
    print(f"[*] Output dir:  {RUN_DIR.relative_to(REPO_ROOT)}")
    print()

    scripts = sorted(LABS_DIR.glob("**/src/*.py"))
    scripts = [s for s in scripts if s.name not in SKIP_FILES and not s.name.startswith("_")]

    written = 0
    for s in scripts:
        config_name = script_to_display_name(s)
        config_file = RUN_DIR / script_to_config_filename(s)
        folder = script_to_folder_name(s)
        rel_path = s.relative_to(REPO_ROOT).as_posix()

        xml = TEMPLATE.format(
            name=config_name,
            folder=folder,
            module=module,
            script_path=rel_path,
        )
        config_file.write_text(xml, encoding="utf-8")
        written += 1
        print(f"  [+] {config_name:50s}  -> {config_file.name}")

    print()
    print(f"[OK] Generated {written} run configurations.")
    print()
    print("Next steps:")
    print("  1. Open PyCharm, File → Settings → Project → Python Interpreter")
    print("     → Add Local Interpreter → Existing → .venv\\Scripts\\python.exe")
    print("  2. PyCharm auto-detects .run/*.run.xml — see top-right dropdown")
    print("  3. Pick any 'ch0X · NN_xxx' from dropdown, click Run ▶")
    return 0


if __name__ == "__main__":
    sys.exit(main())
