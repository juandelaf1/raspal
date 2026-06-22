# RASPAL Public API Reference

> Version: 0.6.0 (stable)
> La API pública documentada aquí sigue [SemVer](https://semver.org/).
> No se introducen cambios incompatibles en versiones MINOR o PATCH.

## Convención de versionado

- **PATCH** (0.6.x): solo bug fixes
- **MINOR** (0.x.0): nuevas funcionalidades, compatible hacia atrás
- **MAJOR** (x.0.0): cambios incompatibles (con deprecation warnings)

---

## Clases principales

### `Fetcher`

Motor de fetching multi-engine con caché y throttle.

```python
from raspal import Fetcher

f = Fetcher()
result = f.fetch("https://example.com", engine="auto", cache_ttl=3600, timeout=30)
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL a fetchear |
| `engine` | `str` | `"auto"` | `"scrapling"`, `"playwright"`, `"stealth"`, `"auto"` |
| `cache_ttl` | `int` | `3600` | TTL en segundos (0 = sin caché) |
| `timeout` | `int` | `30` | Timeout en segundos |

### `AsyncFetcher`

Versión asíncrona con ProcessPoolExecutor para Playwright.

```python
from raspal import AsyncFetcher

async with AsyncFetcher(max_workers=8) as fetcher:
    result = await fetcher.fetch_async("https://example.com")
    results = await fetcher.fetch_batch(["https://a.com", "https://b.com"])
```

### `Extractor`

Extracción de texto, metadata y selectores CSS.

```python
from raspal import Extractor

ext = Extractor()
text = ext.extract_text(html)
meta = ext.extract_metadata(html)
data = ext.extract_selectors(html, {"title": "h1", "price": ".price"})
data = ext.extract_selectors_fast(html, {"title": "h1"})  # con selectolax
```

### `LLMExtractor`

Extracción estructurada con IA local (Ollama).

```python
from raspal import LLMExtractor

llm = LLMExtractor()
data = llm.extract(text, template="product")
data = llm.extract(text, config=LLMConfig(template="product", strict=True))
results = llm.extract_batch([text1, text2], template="article")
chain_result = llm.extract_chain(text, chain_steps)
```

**Templates predefinidos:** `product`, `article`, `person`, `review`, `event`, `generic`

### `Cache`

Caché SQLite con TTL configurable.

```python
from raspal import Cache

with Cache("cache.sqlite") as cache:
    cache.get(url, ttl=3600)   # → str | None
    cache.set(url, html)       # → None
    cache.clear(url)           # → None (clear specific)
    cache.clear()              # → None (clear all)
```

### `Pipeline`

Colección de resultados con exportación JSON/CSV.

```python
from raspal import Pipeline

p = Pipeline()
p.add(url="https://...", data={"title": "..."})
p.to_json("results.json")
p.to_csv("results.csv")
```

### `RequestQueue`

Cola persistente SQLite con prioridades y reintentos.

```python
from raspal import RequestQueue

q = RequestQueue("queue.sqlite")
q.push(url, priority=1, max_retries=3)
item = q.pop()       # → QueueItem | None
q.complete(item)
q.retry(item, reason)
q.pending_count()
q.failed_count()
```

### `Router`

Orquestador de pipelines desde YAML.

```python
from raspal import Router

router = Router()
result = router.run("config.yaml")
result = await router.run_async("config.yaml")
pipeline = router.run_queue("config.yaml", "queue.sqlite")
```

---

## Modelos de datos

### `FetchResult`

```python
from raspal.models import FetchResult

FetchResult(
    url: str,
    status: int,
    html: str | None = None,
    engine: str = "scrapling",
    cached: bool = False,
    error: str | None = None,
)
```

### `LLMConfig`

```python
from raspal.models import LLMConfig

LLMConfig(
    model: str = "llama3.2",
    prompt: str = "",
    output_schema: dict | None = None,
    template: str = "",
    temperature: float = 0.0,
    strict: bool = False,
    timeout: int = 60,
)
```

### `PipelineConfig` (config YAML completa)

```python
from raspal.models import PipelineConfig, ExtractionConfig, ThrottleConfig, ProxyConfig
```

---

## Excepciones

```python
from raspal import RaspalError, FetchError, ExtractError, LLMError, ConfigError

try:
    result = fetcher.fetch(url)
except FetchError as e:
    ...
```

| Excepción | Base | Uso |
|-----------|------|-----|
| `RaspalError` | `Exception` | Base de todas |
| `FetchError` | `RaspalError` | Error de fetching |
| `TimeoutError` | `FetchError` | Timeout |
| `HTTPError` | `FetchError` | HTTP error (status, url) |
| `ConnectionError` | `FetchError` | Conexión fallida |
| `ProxyError` | `FetchError` | Proxy fallido |
| `ExtractError` | `RaspalError` | Error de extracción |
| `LLMError` | `RaspalError` | Error de LLM |
| `CacheError` | `RaspalError` | Error de caché |
| `QueueError` | `RaspalError` | Error de cola |
| `ConfigError` | `RaspalError` | Error de configuración |

---

## Funciones auxiliares

```python
from raspal import check_compliance

result = check_compliance("https://example.com")
# → {"signals": {...}, "warnings": [...]}
```

---

## CLI

```bash
raspal fetch <url>           # Scrapear URL
raspal run <config.yaml>     # Ejecutar pipeline YAML
raspal queue <config.yaml>   # Ejecutar con cola
raspal compliance <url>      # Verificar robots.txt
raspal validate <config.yaml> # Validar YAML
raspal setup                 # Instalar browsers + Ollama
raspal init                  # Scaffold proyecto
raspal doctor                # Diagnosticar entorno
raspal demo                  # Demo sin configuración
raspal serve                 # Dashboard web (puerto 8462)
raspal report                # Generar reporte HTML
raspal status                # Estado del sistema
raspal clear-cache           # Limpiar caché
raspal version               # Versión instalada
```
