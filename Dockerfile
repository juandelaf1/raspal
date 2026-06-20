# RΛSPΛL SCRAPER — Dockerfile
# Imagen optimizada para scraping con IA local

FROM python:3.11-slim

# ============================================
# 1. Sistema base para Playwright
# ============================================
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Instalar dependencias del sistema en una sola capa
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    git \
    build-essential \
    # Dependencias de Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libx11-6 \
    libxrender1 \
    libxshmfence1 \
    # Utilidades para debugging
    procps \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# 2. Usuario no-root para seguridad
# ============================================
RUN groupadd --gid 10001 raspal \
    && useradd --uid 10001 --gid raspal --create-home --shell /bin/bash raspal

# ============================================
# 3. Dependencias Python
# ============================================
WORKDIR /app

# Copiar primero los archivos de metadata para aprovechar cache
COPY pyproject.toml ./
COPY src/ ./src/

# Instalar el paquete en modo desarrollo para permitir hot-reload
RUN pip install --upgrade pip \
    && pip install -e .[all] \
    && python -m playwright install chromium

# ============================================
# 4. Volúmenes y permisos
# ============================================
RUN mkdir -p /data /pipelines /ms-playwright \
    && chown -R raspal:raspal /data /pipelines /ms-playwright /app

USER raspal

# ============================================
# 5. Variables de entorno
# ============================================
ENV OLLAMA_HOST=http://ollama:11434 \
    RASPAL_DATA_DIR=/data \
    RASPAL_PIPELINES_DIR=/pipelines \
    PATH="/home/raspal/.local/bin:${PATH}"

# ============================================
# 6. Punto de entrada
# ============================================
COPY docker/entrypoint.sh /usr/local/bin/raspal-entrypoint
RUN chmod +x /usr/local/bin/raspal-entrypoint

ENTRYPOINT ["raspal-entrypoint"]
CMD ["raspal", "--help"]
