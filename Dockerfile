# ============ Douyin_TikTok_Download_API Docker 镜像 ============
# 基于官方 python:3.11-slim，适配 Windows / Linux Docker

FROM python:3.11-slim-bookworm

LABEL maintainer="Evil0ctal"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------- 1. 安装依赖（利用 Docker 缓存）----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# ---------- 2. 复制应用代码 ----------
COPY app/ ./app/
COPY crawlers/ ./crawlers/
COPY config.yaml .
COPY start.py .

# ---------- 3. 创建运行时目录 ----------
RUN mkdir -p /app/logs /app/download

VOLUME ["/app/logs", "/app/download"]

EXPOSE 8080

# ---------- 4. 启动 ----------
CMD ["python", "start.py"]
