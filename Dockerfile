FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3-pip git curl && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# 升级 pip 并安装依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.5.1 \
    vllm==0.6.6.post1 \
    accelerate \
    fastapi \
    uvicorn[standard] \
    flask \
    flask-cors \
    flasgger \
    gunicorn \
    gevent \
    openai \
    fastmcp \
    huggingface_hub

# 安装最新 transformers
RUN pip install --no-cache-dir git+https://github.com/huggingface/transformers.git

# 复制应用代码
COPY app.py app_fastapi.py mcp_server.py ./
COPY templates/ templates/
COPY static/ static/

# 创建数据目录
RUN mkdir -p /app/models /tmp/hy-mt

EXPOSE 8021

# 使用 uvicorn 运行 FastAPI
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8021"]
