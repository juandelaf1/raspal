# RΛSPΛL SCRAPER — Docker

Web scraping con IA local. Scrapling + Playwright + Ollama.

## Quickstart

```bash
# Sin clonar nada
docker run --rm -it \
  -v $(pwd)/data:/data \
  -v $(pwd)/pipelines:/pipelines \
  juandelaf/raspal:latest raspal demo
```

## Con docker-compose

```bash
# 1. Descargar compose
curl -O https://raw.githubusercontent.com/juandelaf1/RASPAL_SCRAPER/master/docker-compose.yml

# 2. Arrancar
docker compose up -d

# 3. Demo
docker compose run raspal raspal demo
```

## Docs

- [Quickstart Docker](https://github.com/juandelaf1/RASPAL_SCRAPER/blob/master/docs/quickstart-docker.md)
- [Legal & Ethics](https://github.com/juandelaf1/RASPAL_SCRAPER/blob/master/docs/legal-and-ethics.md)
- [Known Issues](https://github.com/juandelaf1/RASPAL_SCRAPER/blob/master/KNOWN_ISSUES.md)

## License

MIT
