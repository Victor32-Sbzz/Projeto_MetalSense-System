# ==============================================================================
# ESTÁGIO 1: BUILDER — Frontend (Vite + React) + Python deps
# ==============================================================================
FROM node:20-alpine AS web-builder
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim AS py-builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# ESTÁGIO 2: RUNTIME FINAL
# ==============================================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="TechForge <contato@techforge.io>"
LABEL description="MetalSense - Gateway Industrial IoT + Web (React)"
LABEL version="3.0.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq5 && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 10001 metalsense && \
    useradd -u 10001 -g metalsense -s /bin/bash -m metalsense

WORKDIR /app
COPY --from=py-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=metalsense:metalsense . /app
# Copia build do frontend para dentro da imagem
COPY --from=web-builder --chown=metalsense:metalsense /web/dist /app/web/dist

RUN mkdir -p /app/data /app/logs && chown -R metalsense:metalsense /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    METALSENSE_ENV=production \
    PORT=5000 \
    GUNICORN_BIND=0.0.0.0:5000

USER metalsense
EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "-c", "gunicorn_conf.py", "api:create_app()"]
