FROM python:3.11-slim
WORKDIR /app

RUN pip install chromadb
EXPOSE 8000

CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-config", "chromadb/log_config.yml", "--proxy-headers", "--timeout-keep-alive", "120" ]
