from typing import Self

from raspal.cache import Cache
from raspal.exceptions import FetchError, TimeoutError
from raspal.models import FetchResult, ProxyConfig
from raspal.throttle import AutoThrottle


class Fetcher:
    STATIC = "scrapling"
    DYNAMIC = "playwright"
    STEALTH = "stealth"

    def __init__(
        self,
        cache: Cache | None = None,
        throttle: AutoThrottle | None = None,
        proxy: ProxyConfig | None = None,
    ):
        self.cache = cache or Cache()
        self.throttle = throttle or AutoThrottle()
        self.proxy = proxy
        self._browser = None
        self._configure_scrapling()

    @staticmethod
    def _configure_scrapling():
        from scrapling import Fetcher as ScraplingFetcher

        ScraplingFetcher.configure(huge_tree=True, adaptive=True)

    def _get_proxy_kwargs(self) -> dict:
        if not self.proxy:
            return {}
        if self.proxy.http:
            return {
                "proxies": {
                    "http": self.proxy.http,
                    "https": self.proxy.https or self.proxy.http,
                }
            }
        return {}

    def fetch(
        self,
        url: str,
        engine: str = "auto",
        cache_ttl: int = 3600,
        timeout: int = 30,
        **kwargs,
    ) -> FetchResult:
        engine = self._resolve_engine(url, engine)
        self.throttle.wait(engine)

        if self.cache:
            try:
                cached = self.cache.get(url, ttl=cache_ttl)
                if cached is not None:
                    return FetchResult(
                        url=url, status=200, html=cached, cached=True, engine=engine
                    )
            except Exception:
                pass

        result = self._dispatch(url, engine, timeout, kwargs)

        if self.cache and result.html and result.status == 200:
            try:
                self.cache.set(url, result.html)
            except Exception:
                pass

        self.throttle.record(engine, result.status)
        return result

    def _resolve_engine(self, url: str, preferred: str) -> str:
        if preferred != "auto":
            return preferred
        if url.startswith("http://") or url.startswith("https://"):
            return self.STATIC
        return self.STATIC

    def _dispatch(self, url: str, engine: str, timeout: int, kwargs: dict) -> FetchResult:
        dispatch = {
            self.STATIC: self._fetch_static,
            self.DYNAMIC: self._fetch_dynamic,
            self.STEALTH: self._fetch_stealth,
        }
        handler = dispatch.get(engine, self._fetch_static)
        try:
            return handler(url, timeout, kwargs)
        except FetchError:
            raise
        except Exception as e:
            return FetchResult(url=url, status=0, error=str(e), engine=engine)

    def _fetch_static(self, url: str, timeout: int, kwargs: dict) -> FetchResult:
        from scrapling import Fetcher as ScraplingFetcher

        proxy = self._get_proxy_kwargs()
        resp = ScraplingFetcher.get(url, timeout=timeout, **proxy, **kwargs)
        html = resp.html_content
        if html is None and hasattr(resp, "body"):
            try:
                html = resp.body.decode()
            except Exception:
                pass
        return FetchResult(
            url=url,
            status=resp.status,
            html=html,
            engine=self.STATIC,
            metadata={"headers": dict(resp.headers)},
        )

    def _fetch_dynamic(self, url: str, timeout: int, kwargs: dict) -> FetchResult:
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from scrapling.fetchers import DynamicFetcher

        opts = {
            "headless": True,
            "disable_resources": True,
            "network_idle": True,
            "load_dom": True,
            "block_ads": True,
            "timeout": timeout * 1000,
            **kwargs,
        }
        proxy = self._get_proxy_kwargs()
        if proxy:
            opts["proxy"] = proxy.get("proxies", {}).get("http")

        try:
            resp = DynamicFetcher.fetch(url, **opts)
        except PlaywrightTimeout:
            raise TimeoutError(f"Playwright timed out after {timeout}s for {url}. Prueba con --engine scrapling (mas rapido) o aumenta el timeout con --timeout 60.") from None
        except Exception as e:
            msg = str(e)
            if "browser" in msg.lower() or "executable" in msg.lower():
                hint = "Playwright browser no instalado. Ejecuta: python -m playwright install chromium"
            elif "connect" in msg.lower() or "refused" in msg.lower():
                hint = f"No se pudo conectar con {url}. Verifica la URL y tu conexion."
            else:
                hint = f"Prueba con --engine scrapling (mas estable) o --engine stealth (si el sitio tiene protecciones)."
            raise FetchError(f"Dynamic fetch fallo para {url}: {msg}. {hint}") from e

        html = resp.html_content
        if html is None and hasattr(resp, "body"):
            try:
                html = resp.body.decode()
            except Exception:
                pass
        return FetchResult(
            url=url,
            status=resp.status,
            html=html,
            engine=self.DYNAMIC,
            metadata={"headers": dict(resp.headers)},
        )

    def _fetch_stealth(self, url: str, timeout: int, kwargs: dict) -> FetchResult:
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from scrapling.fetchers import StealthyFetcher

        opts = {
            "headless": True,
            "disable_resources": True,
            "network_idle": True,
            "load_dom": True,
            "block_ads": True,
            "solve_cloudflare": True,
            "timeout": timeout * 1000,
            **kwargs,
        }
        proxy = self._get_proxy_kwargs()
        if proxy:
            opts["proxy"] = proxy.get("proxies", {}).get("http")

        try:
            resp = StealthyFetcher.fetch(url, **opts)
        except PlaywrightTimeout:
            raise TimeoutError(f"Stealth timed out after {timeout}s for {url}. El modo stealth es mas lento por las protecciones anti-bot. Prueba con --engine playwright si el sitio no requiere stealth.") from None
        except Exception as e:
            msg = str(e)
            if "browser" in msg.lower() or "executable" in msg.lower():
                hint = "Playwright browser no instalado. Ejecuta: python -m playwright install chromium"
            elif "connect" in msg.lower() or "refused" in msg.lower():
                hint = f"No se pudo conectar con {url}. Verifica la URL."
            else:
                hint = "Prueba con --engine playwright o --engine scrapling como alternativa."
            raise FetchError(f"Stealth fetch fallo para {url}: {msg}. {hint}") from e

        html = resp.html_content
        if html is None and hasattr(resp, "body"):
            try:
                html = resp.body.decode()
            except Exception:
                pass
        return FetchResult(
            url=url,
            status=resp.status,
            html=html,
            engine=self.STEALTH,
            metadata={"headers": dict(resp.headers)},
        )

    def close(self):
        self.throttle.close()
        try:
            self.cache.close()
        except Exception:
            pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.close()
