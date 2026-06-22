# Changelog

## [0.6.1] — 2026-06-22

### Fixed
- README banner uses absolute raw URL so PyPI renders it correctly
- CLI examples use hyphens (`async-fetch`, `clear-cache`) instead of underscores
- Added missing `raspal doctor` and `raspal version` to README

### Changed
- pyproject.toml version bumped to 0.6.1
- Trusted publishing configured on PyPI for CI/CD automation

## [0.6.0] — 2026-06-22

### Added
- `raspal doctor` — full environment diagnostics
- `raspal demo` — demo with books.toscrape.com + optional AI
- CI workflow (pytest + ruff on every push)
- `PUBLIC_API.md` — stable public API contract
- `CONTRIBUTING.md` — contribution guidelines
- `SECURITY.md` — security policy
- Tests: CLI, Compliance, Async modules (+13 new tests)
- CI badges in README

### Changed
- Compliance checker now parses real robots.txt (urllib.robotparser)
- Router refactored: `_extract()` eliminates ~70% code duplication
- Versioning policy documented (SemVer)
- All tests use mocks — no external dependencies needed

### Fixed
- `test_fetch_unknown_url` no longer makes real HTTP requests

## [0.5.0] — 2026-06-21

### Added
- Docker support (Dockerfile, docker-compose.yml, docker-compose.dev.yml)
- `raspal compliance` — check robots.txt and sensitive domains
- `raspal validate` — validate YAML config files
- Compliance module (`raspal.compliance`)
- Legal and ethics documentation (`docs/legal-and-ethics.md`)
- Docker quickstart guide (`docs/quickstart-docker.md`)
- KNOWN_ISSUES.md documenting limitations
- Example YAML pipelines (e-commerce, news, real estate)
- Multi-arch Docker CI (GitHub Actions for amd64 + arm64)
- requirements.txt for reproducible installs

### Changed
- README reorganized with Docker as primary installation path
- Updated AGENTS.md with new commands

## [0.4.0] — 2026-06-19

### Added
- `raspal setup` — installs Playwright browsers, verifies Ollama
- `raspal init` — interactive project scaffolding
- `raspal report` — HTML report generation
- `raspal serve` — web dashboard (FastAPI + uvicorn)
- AsyncFetcher improvements
- Web dashboard with real-time scraping

### Changed
- Project renamed to RASPAL SCRAPER
- Complete README rewrite

## [0.3.0] — 2026-06-19

### Added
- YAML pipeline support
- LLM extraction chain (multi-step)
- Output schema validation
- Request queue with priorities and retries

## [0.2.0] — 2026-06-19

### Added
- AsyncFetcher for concurrent scraping
- CLI commands (async_fetch, async_batch, status, clear_cache)
- Enhanced documentation

## [0.1.0] — 2026-06-19

### Added
- Initial release
- Fetcher with multiple engines (scrapling, playwright, stealth)
- Cache with TTL
- AutoThrottle for rate limiting
- Extractor with text and metadata extraction
- LLM extraction via Ollama
- Basic CLI (fetch, run, queue)
