# Post para r/webscraping — Listo para publicar

## Título

I built a CLI that scrapes any URL and extracts structured data with local AI — no API keys, no data leaving your machine (Docker, open source)

## Cuerpo

```
TL;DR: pip install raspal (or Docker) → raspar fetch URL → structured JSON. 
All local, all private. https://github.com/juandelaf1/RASPAL_SCRAPER

I was tired of stitching together a dozen different tools every time I needed 
structured data from a website. Scrapy for scraping, BeautifulSoup for parsing,
OpenAI for structuring — and sending all my data to third parties.

Built RASPAL SCRAPER instead:

• 3 engines: Scrapling (fast), Playwright (JS), Stealth (anti-bot)
• Local AI extraction via Ollama — no API keys, no data leaks
• CLI + YAML pipelines + web dashboard + Docker
• Built-in cache, auto-throttle, request queue with priorities
• Compliance checker (robots.txt, sensitive domains)

The pitch in one command:
  docker compose up -d
  docker compose run raspal raspal run config.yaml
  → structured JSON

It's MIT licensed. Would love feedback on:
• The onboarding experience (Docker vs pip install)
• What use cases I'm missing
• How it compares to your current stack

Repo: https://github.com/juandelaf1/RASPAL_SCRAPER
```

## Reglas de publicación

- Publicar un lunes, martes o miércoles por la mañana (US time)
- Responder TODOS los comentarios en las primeras 6 horas
- Si alguien reporta un bug, agradecer públicamente y decir qué vas a hacer
- No borrar comentarios negativos
