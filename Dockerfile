# 企业知识库问答机器人 — Docker 部署

FROM python:3.11-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/chroma_db data/documents

EXPOSE 8501 8000

# 默认启动 Streamlit
CMD ["python", "run_app.py"]
