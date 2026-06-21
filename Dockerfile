# RASPAL SCRAPER — Dockerfile (multi-stage)
# Imagen optimizada para scraping con IA local
# Stage 1: builder (instala dependencias Python y Playwright)
# Stage 2: final (solo runtime, sin build tools)

# ============================================
# STAGE 1 — Builder con dependencias de build
# ============================================
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    git \
    build-essential \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 \
    libcairo2 libatspi2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcb1 libxext6 libx11-6 libxrender1 libxshmfence1 \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md CHANGELOG.md ./
COPY src/ ./src/

RUN pip install --upgrade pip \
    && pip install --no-compile .[all] \
    && python -m playwright install chromium 2>/dev/null; true \
    && find /usr/local/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true

# ============================================
# STAGE 2 — Imagen final (minima)
# ============================================
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=0

# Solo runtime deps (sin build-essential, git, gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 \
    libcairo2 libatspi2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcb1 libxext6 libx11-6 libxrender1 libxshmfence1 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copiar Python packages y scripts desde builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/raspal* /usr/local/bin/

# Limpiar pycache y archivos sobrantes
RUN find /usr/local/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true \
    && rm -rf /usr/local/lib/python3.11/site-packages/pip /usr/local/lib/python3.11/site-packages/setuptools* /usr/local/lib/python3.11/site-packages/wheel* /root/.cache

# Crear usuario no-root
RUN groupadd --gid 10001 raspal \
    && useradd --uid 10001 --gid raspal --create-home --shell /bin/bash raspal

WORKDIR /app
RUN mkdir -p /data /pipelines && chown -R raspal:raspal /data /pipelines /app

COPY docker/entrypoint.sh /usr/local/bin/raspal-entrypoint
RUN chmod +x /usr/local/bin/raspal-entrypoint

USER raspal

ENV OLLAMA_HOST=http://ollama:11434 \
    RASPAL_DATA_DIR=/data \
    RASPAL_PIPELINES_DIR=/pipelines \
    PATH="/home/raspal/.local/bin:${PATH}"

ENTRYPOINT ["raspal-entrypoint"]
CMD ["raspal", "--help"]
