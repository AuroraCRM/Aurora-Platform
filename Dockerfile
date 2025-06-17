# Dockerfile com segurança reforçada para Aurora-Platform
# Usa multi-stage build para reduzir a superfície de ataque

# Estágio de build
FROM python:3.11-slim AS builder

# Evita mensagens de aviso durante a instalação
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Cria usuário não-root para segurança
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Instala dependências de build
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Cria e ativa ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia apenas os arquivos necessários para instalar dependências
WORKDIR /app
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Estágio final
FROM python:3.11-slim

# Define variáveis de ambiente para segurança
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    ENVIRONMENT="production" \
    DEBUG="False"

# Cria usuário não-root para segurança
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Copia o ambiente virtual do estágio de build
COPY --from=builder /opt/venv /opt/venv

# Cria diretórios necessários com permissões corretas
RUN mkdir -p /app/logs /app/certs && \
    chown -R appuser:appuser /app

# Copia o código da aplicação
WORKDIR /app
COPY --chown=appuser:appuser . .

# Configurações de segurança
RUN chmod 600 .env* && \
    chmod 700 certs && \
    chmod 600 certs/* && \
    chmod 755 run_api.py

# Verifica vulnerabilidades conhecidas
RUN pip install safety && \
    safety check

# Muda para o usuário não-root
USER appuser

# Expõe a porta da API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar a aplicação
CMD ["python", "run_api.py"]