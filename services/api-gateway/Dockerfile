FROM python:3.11-slim

WORKDIR /repo/services/api-gateway

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/api-gateway/requirements.txt ./
RUN pip install --default-timeout=120 --no-cache-dir -r requirements.txt

COPY services/api-gateway /repo/services/api-gateway
COPY services/market-data /repo/services/market-data
COPY services/ai-engine /repo/services/ai-engine
COPY services/crawler /repo/services/crawler
COPY services/browser-automation /repo/services/browser-automation

RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
