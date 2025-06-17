# 使用 Python 3.10 作為基礎映像
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安裝系統依賴
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 複製專案文件
COPY requirements.txt .
COPY setup.py .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

# 複製應用程序代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
