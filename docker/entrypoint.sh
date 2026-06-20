#!/bin/bash
set -euo pipefail

# ============================================
# RΛSPAL SCRAPER — Docker Entrypoint
# ============================================
# Verifica Ollama, descarga el modelo si hace falta,
# y ejecuta el comando que el usuario haya pasado.

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
TIMEOUT=30

echo "╔════════════════════════════════════════╗"
echo "║   RΛSPΛL SCRAPER — Docker Edition    ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Version: $(raspal --version 2>/dev/null || echo 'unknown')"
echo "Ollama:  ${OLLAMA_HOST}"
echo "Modelo:  ${MODEL}"
echo ""

# ============================================
# 1. Verificar que Ollama esté accesible
# ============================================
echo "🔍 Verificando conexión con Ollama..."
for i in $(seq 1 $TIMEOUT); do
    if curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
        echo "✅ Ollama conectado"
        break
    fi
    if [ "$i" -eq "$TIMEOUT" ]; then
        echo "❌ Error: no se pudo conectar a Ollama en ${OLLAMA_HOST}"
        echo ""
        echo "Pasos para solucionarlo:"
        echo "  1. Verifica que el servicio 'ollama' esté corriendo"
        echo "  2. Ejecuta: docker compose ps"
        echo "  3. Si hace falta, reinicia: docker compose restart ollama"
        exit 1
    fi
    echo "   Esperando a Ollama... (${i}/${TIMEOUT})"
    sleep 2
done

# ============================================
# 2. Descargar modelo si no existe
# ============================================
if ! ollama list | grep -q "${MODEL%%:*}"; then
    echo ""
    echo "📦 Modelo '${MODEL}' no encontrado. Descargando..."
    echo "   Esto puede tardar varios minutos (2-4 GB)."
    ollama pull "${MODEL}"
    echo "✅ Modelo '${MODEL}' descargado"
else
    echo "✅ Modelo '${MODEL}' ya está disponible"
fi

# ============================================
# 3. Mensaje de bienvenida
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  RASPAL SCRAPER listo para usar"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comandos útiles:"
echo "  raspal demo                          # Demo con una URL pública"
echo "  raspal fetch https://ejemplo.com     # Fetch básico"
echo "  raspal run pipelines/config.yaml     # Ejecutar tu pipeline"
echo "  raspal init                          # Crear proyecto YAML"
echo "  raspal --help                        # Ver todos los comandos"
echo ""

# ============================================
# 4. Ejecutar comando del usuario o mostrar ayuda
# ============================================
if [ "$#" -eq 0 ]; then
    raspal --help
else
    exec "$@"
fi
