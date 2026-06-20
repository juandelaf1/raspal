#!/bin/bash
set -euo pipefail

# ============================================
# RΛSPΛL SCRAPER — Ollama Init
# ============================================
# Espera a que Ollama esté listo y descarga el modelo por defecto.

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
TIMEOUT=60

echo "🔍 Esperando a que Ollama esté listo..."
for i in $(seq 1 $TIMEOUT); do
    if curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
        echo "✅ Ollama listo"
        break
    fi
    if [ "$i" -eq "$TIMEOUT" ]; then
        echo "❌ Error: Ollama no respondió en ${TIMEOUT}s"
        exit 1
    fi
    sleep 2
done

# Descargar modelo si no existe
if ! ollama list | grep -q "${MODEL%%:*}"; then
    echo "📦 Descargando modelo '${MODEL}'..."
    ollama pull "${MODEL}"
    echo "✅ Modelo '${MODEL}' descargado"
else
    echo "✅ Modelo '${MODEL}' ya está disponible"
fi

# Verificar que el modelo responde
echo "🧪 Probando el modelo con un prompt simple..."
response=$(ollama run "${MODEL}" "Responde solo OK" | head -n 1)
if [ "$response" = "OK" ]; then
    echo "✅ Modelo funciona correctamente"
else
    echo "⚠️  El modelo respondió, pero el output no fue el esperado"
    echo "   Respuesta: ${response}"
fi

echo "✅ Ollama inicializado correctamente"
