#!/bin/bash
set -euo pipefail

# ============================================
# RΛSPΛL SCRAPER — Healthcheck
# ============================================
# Verifica que Ollama y RASPAL estén funcionando correctamente.

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"

# Verificar Ollama
if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
    echo "❌ Ollama no responde en ${OLLAMA_HOST}"
    exit 1
fi

# Verificar que hay al menos un modelo disponible
if ! ollama list | grep -q .; then
    echo "❌ No hay modelos de Ollama instalados"
    exit 1
fi

# Verificar que RASPAL está disponible
if ! command -v raspal >/dev/null 2>&1; then
    echo "❌ El comando 'raspal' no está disponible"
    exit 1
fi

echo "✅ RASPAL SCRAPER está saludable"
exit 0
