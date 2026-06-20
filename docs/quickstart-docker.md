# Quickstart with Docker

The fastest way to try RASPAL SCRAPER is with Docker. No Python installation, no manual dependency setup, no hassle.

## Prerequisites

- Docker installed and running
- 4GB+ free disk space (for the Ollama model)

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/juandelaf1/RASPAL_SCRAPER.git
cd RASPAL_SCRAPER

# 2. Start everything (Ollama + RASPAL)
docker compose up -d

# 3. Run the demo
docker compose run raspal raspal demo
```

## What happens?

1. **Ollama** downloads and starts (~2-4 GB)
2. **RASPAL** container builds and starts
3. The default model (`llama3.2:3b`) is pulled automatically
4. You're ready to scrape

## Expected output

```
╔════════════════════════════════════════╗
║   RΛSPΛL SCRAPER — Docker Edition    ║
╚════════════════════════════════════════╝

Version: 0.4.0
Ollama:  http://ollama:11434
Modelo:  llama3.2:3b

🔍 Verificando conexión con Ollama...
✅ Ollama conectado
📦 Modelo 'llama3.2:3b' no encontrado. Descargando...
...
✅ Modelo 'llama3.2:3b' descargado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RASPAL SCRAPER listo para usar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Next steps

- Create your first pipeline: `raspal init`
- Run a custom YAML: `raspal run pipelines/mi-config.yaml`
- Generate a report: `raspal report --input results.json --output report.html`
- Start the dashboard: `raspal serve --host 0.0.0.0 --port 8462`

## Troubleshooting

### "Ollama no responde"

Run `docker compose ps` to check the status. If needed:

```bash
docker compose restart ollama
```

### "No space left on device"

The Ollama model needs ~2-4 GB. Free up disk space or use a lighter model:

```bash
docker compose run -e OLLAMA_MODEL=llama3.2:1b raspal raspal demo
```

### "Permission denied" on Windows

Make sure you're running from WSL2 or a directory where Docker has write access.
