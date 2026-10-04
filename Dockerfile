# ==============================================================================
# ESTÁGIO 1: BUILDER (Compilação e Instalação de Dependências)
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# ESTÁGIO 2: RUNTIME FINAL (Imagem Leve e Segura para Produção)
# ==============================================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="TechForge <contato@techforge.io>"
LABEL description="MetalSense - Gateway Industrial IoT e Monitoramento Preditivo"
LABEL version="2.0.0-PRO"

# Instala apenas dependências de runtime mínimas necessárias (ex: curl para probes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário sem privilégios de root (Princípio do Menor Privilégio)
RUN groupadd -g 10001 metalsense && \
    useradd -u 10001 -g metalsense -s /bin/bash -m metalsense

WORKDIR /app

# Copia ambiente virtual pré-construído
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código-fonte da aplicação
COPY --chown=metalsense:metalsense . /app

# Cria diretórios de dados e logs com permissões adequadas
RUN mkdir -p /app/data /app/logs && \
    chown -R metalsense:metalsense /app

# Variáveis padrão de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    METALSENSE_ENV=production \
    PORT=5000 \
    GUNICORN_BIND=0.0.0.0:5000

# Execução como usuário restrito (non-root)
USER metalsense

EXPOSE 5000 8501

# Healthcheck interno do container
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando padrão: inicia o servidor WSGI Gunicorn
CMD ["gunicorn", "-c", "gunicorn_conf.py", "api:create_app()"]
