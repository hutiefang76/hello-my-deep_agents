# ============================================================
# hello-my-deep_agents · Dockerfile
# Python 3.11 (避免 3.14 的 langchain Pydantic 兼容警告)
# ============================================================

FROM python:3.11-slim AS base

# 元数据
LABEL maintainer="frank.hutiefang"
LABEL description="DeepAgents 教程统一运行时 — Python 3.11 + 全部依赖"

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 配 pip 国内源加速 (用户在国内)
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com \
    && pip install --no-cache-dir --upgrade pip

# 先装依赖 (单独一层利用缓存)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 再 COPY 代码 (代码改动不会破坏依赖层缓存)
COPY . /app

# 默认环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app

# 可选: 暴露 Gradio 端口 (Ch4.1 / Ch4.3)
EXPOSE 7860 7861 8000

# 默认入口: bash (用户自由选 lab 跑)
CMD ["bash"]
