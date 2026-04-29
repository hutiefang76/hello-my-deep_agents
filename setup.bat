@echo off
chcp 65001 >nul 2>&1
REM ============================================================
REM hello-my-deep_agents - Windows one-shot setup
REM ============================================================
REM What it does:
REM   1. Create .venv at project root (Python 3.10+)
REM   2. pip install -r requirements.txt
REM   3. Verify critical imports
REM
REM Usage:
REM   Double-click setup.bat or run from cmd / PowerShell
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   hello-my-deep_agents - Windows setup
echo ============================================================
echo.

REM Step 1: Check Python
echo [1/4] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo    [X] Python not found in PATH. Install Python 3.10+ from https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo    [OK] Python !PYVER! found

REM Step 2: Create .venv
echo.
echo [2/4] Creating .venv ...
if exist ".venv\Scripts\python.exe" (
    echo    [OK] .venv already exists, skip create
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo    [X] venv create failed
        exit /b 1
    )
    echo    [OK] .venv created
)

REM Step 3: Install dependencies
echo.
echo [3/4] Installing dependencies (about 3-5 minutes first time)...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo    [X] pip upgrade failed
    exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo    [X] pip install failed
    exit /b 1
)
echo    [OK] root requirements installed

if exist "labs\ch10-rag-multi-retrieval\requirements.txt" (
    echo    [info] Installing Ch10 extras (rank_bm25 + jieba)...
    .venv\Scripts\python.exe -m pip install -r labs\ch10-rag-multi-retrieval\requirements.txt
)

REM Step 4: Verify imports
echo.
echo [4/4] Verifying critical imports...
.venv\Scripts\python.exe -c "import dotenv, langchain, langgraph, gradio, pydantic; print('   [OK] dotenv / langchain / langgraph / gradio / pydantic')"
if errorlevel 1 (
    echo    [X] import check failed
    exit /b 1
)

REM Check .env
echo.
if not exist ".env" (
    if exist ".env.example" (
        echo [info] .env not found, copying from .env.example
        copy ".env.example" ".env" >nul
        echo    [warn] PLEASE EDIT .env and fill DASHSCOPE_API_KEY
        echo            Apply key: https://bailian.console.aliyun.com/
    )
)

echo.
echo ============================================================
echo   Setup complete!
echo ============================================================
echo.
echo   Next steps:
echo     1. Edit .env, fill DASHSCOPE_API_KEY
echo     2. (Optional) Start middleware: make mw-up
echo     3. Open PyCharm: Settings then Project then Python Interpreter
echo        Add Local Interpreter then Existing then .venv\Scripts\python.exe
echo     4. PyCharm auto-detects .run/*.run.xml (62 configs)
echo        Pick any "ch0X . NN_xxx" from top-right dropdown, click Run
echo.
echo   Full guide: docs\08-PyCharm-config.md
echo.
endlocal
